from lumipy.atlas.atlas import Atlas
from lumipy.atlas.direct_provider_metafactory import _DirectProviderMetafactory
from lumipy.atlas.field_metadata import FieldMetadata
from lumipy.atlas.base.base_provider_factory import BaseProviderFactory
from lumipy.atlas.data_provider_metafactory import _DataProviderMetafactory
from lumipy.client import Client
from typing import List
from lumipy.common.string_utils import random_globe
from pandas import DataFrame
import re
from lumipy.common.string_utils import to_snake_case
from fnmatch import fnmatch
from lumipy.query.expression.sql_value_type import SqlValType


def _query_data_provider_metadata(client: Client) -> DataFrame:
    """Query luminesce for metadata on the available providers.

    Args:
        client (Client): lumipy client to query with.

    Returns:
        DataFrame: pandas dataframe containing query result.
    """

    df = client.query_and_fetch("""
        -- atlas build - data provider query
    
        @data_prov_meta = SELECT
          [Description], [Category], [DocumentationLink], [Type], [Name] AS [TableName], 
          max([LastPingAt]) AS [LastPingAt]
        FROM
          [Sys.Registration]
        WHERE
          [Type] = 'DataProvider'
        GROUP BY
          [Name];

        @data_prov_flds = SELECT
          [FieldName], [TableName], [DataType], [FieldType], [IsMain], [IsPrimaryKey], [ParamDefaultValue], 
          [TableParamColumns], [Description] AS [Description_fld]
        FROM
          [Sys.Field]
        WHERE
          [TableName] IN (SELECT
          [TableName]
        FROM
          @data_prov_meta);

        SELECT
          svc.[Description], svc.[Category], svc.[DocumentationLink], fld.[FieldName], fld.[DataType], fld.[FieldType], 
          fld.[IsMain], fld.[IsPrimaryKey], fld.[ParamDefaultValue], fld.[TableParamColumns], 
          fld.[Description_fld], svc.[TableName] AS [TableName], svc.[Type], svc.[LastPingAt]
        FROM
          @data_prov_meta AS svc 
          LEFT JOIN
        @data_prov_flds AS fld
            ON svc.[TableName] = fld.[TableName]
        WHERE
            fld.[FieldName] IS NOT NULL
    """)

    df['IsMain'] = df.IsMain.astype(bool)
    df['IsPrimaryKey'] = df.IsPrimaryKey.astype(bool)
    return df


def _query_direct_provider_metadata(client: Client) -> DataFrame:
    df = client.query_and_fetch('''
        -- atlas build - direct provider query
        
        SELECT
          [Description], [Type], [DocumentationLink], [Category], [Name] as TableName, 
          max([LastPingAt]) AS [LastPingAt], [CustomSyntax]
        FROM
          Sys.Registration
        WHERE
          [Type] = 'DirectProvider'
          and [Name] NOT IN ('Tools.Pivot', 'Sql.Db', 'Sys.Admin.SetupView')
        GROUP BY
          [Name]
        ORDER BY
          [Name] ASC
    ''')

    def extract_param_table(x):
        if isinstance(x, str):
            return '\n'.join(line for line in x.split('\n') if '│' in line)
        return ''

    def extract_description(x):
        descr = x.CustomSyntax.split(x.ParamTable)[0]
        descr = '\n'.join(descr.split('\n')[:-2])
        return descr.split('<OPTIONS>:')[0]

    def extract_body_str_names(x):
        use_chunks = x.split('enduse;')[0].split('use')[-1].replace('\n', '').split('----')
        use_chunks = [s for s in use_chunks if 'OPTIONS' not in s]
        use_chunks = [re.sub(r'[^A-Za-z0-9 ]+', '', s).strip() for s in use_chunks]
        use_chunks = [to_snake_case(s.replace(' ', '_')) for s in use_chunks if s != '']
        return use_chunks

    df['ParamTable'] = df.CustomSyntax.apply(extract_param_table)
    df = df[df.ParamTable != '']
    df['SyntaxDescr'] = df.apply(extract_description, axis=1)
    df['BodyStrNames'] = df.SyntaxDescr.apply(extract_body_str_names)

    return df


def _build_data_provider_factories(df: DataFrame, client: Client) -> List[BaseProviderFactory]:
    """Build a list of provider metadata objects from the queried metadata rows.

    Args:
        df (DataFrame): dataframe containing the queried luminesce provider metadata.
        client (Client): the client to attach to the provider metadata objects.

    Returns:
        List[BaseProviderFactory]: list of provider metadata objects to build the atlas with.
    """

    factories = []
    for p, p_df in df.groupby('TableName'):
        p_df = p_df.drop_duplicates(subset='FieldName')
        fields = [FieldMetadata.from_row(row) for _, row in p_df.iterrows()]

        p_row = p_df.iloc[0]

        metafactory = _DataProviderMetafactory(
            table_name=p_row.TableName,
            description=p_row.Description,
            provider_type=p_row.Type,
            category=p_row.Category,
            last_ping_at=p_row.LastPingAt,
            documentation=p_row.DocumentationLink,
            fields=fields,
            client=client
        )
        factory = metafactory()

        factories.append(factory)

    return factories


def _parse_direct_provider_help_table(text: str) -> DataFrame:

    df = DataFrame(
        [[c.strip() for c in line.split('│')] for line in text.split('\n')],
        columns=['Argument', 'Description']
    )
    df['Name'] = df.Argument.apply(
        lambda x: x if x != '' else None
    ).ffill().apply(
        lambda x: x.split()[0]
    )

    df = df.groupby('Name', sort=False, as_index=False).agg(
        Description=('Description', 'sum')
    )
    df['Type'] = df.Description.apply(
        lambda x: re.findall('\[.*\]', x)[-1] if 'Regex' in x else re.findall('\[.*?\]', x)[-1]
    ).apply(
        lambda x: x.replace('[', '').replace(']', '')
    ).apply(
        lambda x: x.split('Default:')[0].strip().strip(',')
    ).apply(
        lambda x: 'String' if len(x.split(',')) > 1 else x
    )

    df['DefaultValue'] = df.Description.apply(
        lambda x: re.findall('\[.*\]', x)[-1]
    ).apply(
        lambda x: x.replace('[', '').replace(']', '')
    ).apply(
        lambda x: x.split('Default:')[-1] if 'Default:' in x else None
    )
    return df


def _fixed_shape_direct_provider_columns(table_name):

    def make_column(name, data_type, description):
        return FieldMetadata(
            table_name=table_name,
            field_name=name,
            data_type=data_type,
            field_type='Column',
            is_main=True,
            is_primary_key=True,
            description=description,
            param_default_value=None,
            table_param_columns=None,
        )

    if fnmatch(table_name, '*.RawText*'):
        return [make_column('Content', SqlValType.Text, 'The raw text from the target file.')]

    if fnmatch(table_name, '*.SaveAs*'):
        return [
            make_column('VariableName', SqlValType.Text, 'Name of the @variable saved to a file.'),
            make_column('FileName', SqlValType.Text, 'The file name.'),
            make_column('RowCount', SqlValType.Int, 'The row count of the the @variable saved to a file.'),
            make_column('Skipped', SqlValType.Boolean, 'Whether the @variable was skipped over.'),
        ]

    if table_name in ['Dev.Slack.Send', 'Email.Send']:
        return [
            make_column('Ok', SqlValType.Text, '.'),
            make_column('Request', SqlValType.Text, '.'),
            make_column('Result', SqlValType.Text, '.'),
        ]

    return []


def _build_direct_provider_factories(df: DataFrame, client: Client) -> List[BaseProviderFactory]:
    factories = []
    for _, provider in df.iterrows():

        text = provider.ParamTable
        if text is None or text == '':
            continue

        param_df = _parse_direct_provider_help_table(text)

        fields = [
            FieldMetadata(
                table_name=provider.TableName,
                field_name=param.Name,
                data_type=SqlValType[param.Type],
                field_type='Parameter',
                is_main=False,
                is_primary_key=False,
                description=param.Description,
                param_default_value=param.DefaultValue,
                table_param_columns=None,
            )
            for _, param in param_df.iterrows()
            if to_snake_case(param.Name) not in provider.BodyStrNames
        ]

        fields += _fixed_shape_direct_provider_columns(provider.TableName)

        for i, body_param in enumerate(provider.BodyStrNames):
            fields.append(
                FieldMetadata(
                    table_name=provider.TableName,
                    field_name=body_param,
                    data_type=SqlValType.Text,
                    field_type='Parameter',
                    is_main=False,
                    is_primary_key=False,
                    description='body param placeholder',
                    param_default_value=None,
                    table_param_columns=None,
                    body_param_order=i
                )
            )

        # Instantiate metafactory to build direct provider factory class
        descr_with_syntax = provider.Description
        descr_with_syntax += '\n' + provider.SyntaxDescr.replace(provider.Description, '')
        descr_with_syntax = descr_with_syntax.replace('Of the form', 'Syntax in luminesce SQL is as follows')
        factory_cls = _DirectProviderMetafactory(
            table_name=provider.TableName,
            description=descr_with_syntax,
            provider_type=provider.Type,
            category=provider.Category,
            last_ping_at=provider.LastPingAt,
            documentation=provider.DocumentationLink,
            fields=fields,
            client=client
        )

        # Instantiate factory class to build the direct provider factory instance
        factory = factory_cls()
        factories.append(factory)

    return factories


def get_atlas(**kwargs) -> Atlas:
    """Get luminesce data provider atlas instance by passing any of the following: a token, api_url and app_name; a path to a secrets file
       via api_secrets_filename; or by passing in proxy information. If none of these are provided then lumipy will try
       to find the credentials information as environment variables.

    Keyword Args:
        token (str): Bearer token used to initialise the API
        api_secrets_filename (str): Name of secrets file (including full path)
        api_url (str): luminesce API url
        app_name (str): Application name (optional)
        certificate_filename (str): Name of the certificate file (.pem, .cer or .crt)
        proxy_url (str): The url of the proxy to use including the port e.g. http://myproxy.com:8888
        proxy_username (str): The username for the proxy to use
        proxy_password (str): The password for the proxy to use
        correlation_id (str): Correlation id for all calls made from the returned finbournesdkclient API instances

    Returns:
        Atlas: the atlas instance.
    """

    print(f"Getting atlas{random_globe()}")

    client = Client(**kwargs)

    print("  • Querying data provider metadata...")
    data_df = _query_data_provider_metadata(client)
    print("  • Querying direct provider metadata...")
    direct_df = _query_direct_provider_metadata(client)

    print("  • Building atlas...")
    data_provider_factories = _build_data_provider_factories(data_df, client)
    direct_provider_factories = _build_direct_provider_factories(direct_df, client)

    atlas = Atlas(
        data_provider_factories + direct_provider_factories,
        atlas_type='All available data providers'
    )

    print(f'Done!')
    plist = atlas.list_providers()
    dir_count = len([p for p in plist if p.get_provider_type() == 'DirectProvider'])
    dat_count = len([p for p in plist if p.get_provider_type() == 'DataProvider'])
    print(f"Contents: \n  • {dat_count} data providers\n  • {dir_count} direct providers")

    return atlas
