import unittest
from pypers.steps.fetch.extract.ro.trademarks import Trademarks
from pypers.utils.utils import dict_update
import os
import shutil
from pypers.utils import download
from mock import patch, MagicMock
from pypers.test import mock_db, mockde_db, mock_logger


xml_content = '''<?xml version="1.0" encoding="UTF-8"?>
<Transaction xmlns="http://ro.tmview.europa.eu/trademark/data" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://ro.tmview.europa.eu/trademark/data RO-TM-Search-TradeMark-V1-2.xsd">
  <TransactionHeader>
    <SenderDetails>
      <RequestProducerDateTime>2020-07-01T09:30:04</RequestProducerDateTime>
    </SenderDetails>
  </TransactionHeader>
  <TradeMarkTransactionBody>
    <TransactionContentDetails>
      <TransactionIdentifier>20200701093004</TransactionIdentifier>
      <TransactionCode>RO-TM-Search Trade Mark </TransactionCode>
      <TransactionData>
        <TradeMarkDetails>
          <TradeMark>
            <RegistrationOfficeCode>RO</RegistrationOfficeCode>
            <ApplicationNumber>M 2012 00091</ApplicationNumber>
            <ApplicationDate>2012-01-10</ApplicationDate>
            <RegistrationNumber>119857</RegistrationNumber>
            <RegistrationDate>2012-09-19</RegistrationDate>
            <ApplicationLanguageCode>ro</ApplicationLanguageCode>
            <ExpiryDate>2022-01-10</ExpiryDate>
            <MarkCurrentStatusCode>Registered</MarkCurrentStatusCode>
            <MarkCurrentStatusDate>2016-04-23</MarkCurrentStatusDate>
            <KindMark>Individual</KindMark>
            <MarkFeature>Word</MarkFeature>
            <OppositionPeriodStartDate>2012-01-31</OppositionPeriodStartDate>
            <OppositionPeriodEndDate>2012-03-31</OppositionPeriodEndDate>
            <WordMarkSpecification>
              <MarkVerbalElementText>MSR</MarkVerbalElementText>
            </WordMarkSpecification>
            <MarkImageDetails>
              <MarkImage>
                <MarkImageURI>RO502020000037600.gif</MarkImageURI>
                <MarkImageCategory>
                  <CategoryCodeDetails>
                    <CategoryCode>18.01.01</CategoryCode>
                    <CategoryCode>18.01.01</CategoryCode>
                    <CategoryCode>18.01.01</CategoryCode>
                    <CategoryCode>18.01.01</CategoryCode>
                    <CategoryCode>18.01.01</CategoryCode>
                    <CategoryCode>18.01.02</CategoryCode>
                    <CategoryCode>18.01.02</CategoryCode>
                    <CategoryCode>18.01.02</CategoryCode>
                    <CategoryCode>18.01.02</CategoryCode>
                    <CategoryCode>18.01.02</CategoryCode>
                    <CategoryCode>18.01.03</CategoryCode>
                    <CategoryCode>18.01.03</CategoryCode>
                    <CategoryCode>18.01.03</CategoryCode>
                    <CategoryCode>18.01.03</CategoryCode>
                    <CategoryCode>18.01.03</CategoryCode>
                    <CategoryCode>18.01.05</CategoryCode>
                    <CategoryCode>18.01.05</CategoryCode>
                    <CategoryCode>18.01.05</CategoryCode>
                    <CategoryCode>18.01.05</CategoryCode>
                    <CategoryCode>18.01.05</CategoryCode>
                    <CategoryCode>18.01.07</CategoryCode>
                    <CategoryCode>18.01.07</CategoryCode>
                    <CategoryCode>18.01.07</CategoryCode>
                    <CategoryCode>18.01.07</CategoryCode>
                    <CategoryCode>18.01.07</CategoryCode>
                    <CategoryCode>18.01.08</CategoryCode>
                    <CategoryCode>18.01.08</CategoryCode>
                    <CategoryCode>18.01.08</CategoryCode>
                    <CategoryCode>18.01.08</CategoryCode>
                    <CategoryCode>18.01.08</CategoryCode>
                    <CategoryCode>18.01.09</CategoryCode>
                    <CategoryCode>18.01.09</CategoryCode>
                    <CategoryCode>18.01.09</CategoryCode>
                    <CategoryCode>18.01.09</CategoryCode>
                    <CategoryCode>18.01.09</CategoryCode>
                    <CategoryCode>18.01.11</CategoryCode>
                    <CategoryCode>18.01.11</CategoryCode>
                    <CategoryCode>18.01.11</CategoryCode>
                    <CategoryCode>18.01.11</CategoryCode>
                    <CategoryCode>18.01.11</CategoryCode>
                    <CategoryCode>18.01.12</CategoryCode>
                    <CategoryCode>18.01.12</CategoryCode>
                    <CategoryCode>18.01.12</CategoryCode>
                    <CategoryCode>18.01.12</CategoryCode>
                    <CategoryCode>18.01.12</CategoryCode>
                    <CategoryCode>18.01.14</CategoryCode>
                    <CategoryCode>18.01.14</CategoryCode>
                    <CategoryCode>18.01.14</CategoryCode>
                    <CategoryCode>18.01.14</CategoryCode>
                    <CategoryCode>18.01.14</CategoryCode>
                    <CategoryCode>18.01.15</CategoryCode>
                    <CategoryCode>18.01.15</CategoryCode>
                    <CategoryCode>18.01.15</CategoryCode>
                    <CategoryCode>18.01.15</CategoryCode>
                    <CategoryCode>18.01.15</CategoryCode>
                    <CategoryCode>18.01.16</CategoryCode>
                    <CategoryCode>18.01.16</CategoryCode>
                    <CategoryCode>18.01.16</CategoryCode>
                    <CategoryCode>18.01.16</CategoryCode>
                    <CategoryCode>18.01.16</CategoryCode>
                    <CategoryCode>18.01.17</CategoryCode>
                    <CategoryCode>18.01.17</CategoryCode>
                    <CategoryCode>18.01.17</CategoryCode>
                    <CategoryCode>18.01.17</CategoryCode>
                    <CategoryCode>18.01.17</CategoryCode>
                    <CategoryCode>18.01.18</CategoryCode>
                    <CategoryCode>18.01.18</CategoryCode>
                    <CategoryCode>18.01.18</CategoryCode>
                    <CategoryCode>18.01.18</CategoryCode>
                    <CategoryCode>18.01.18</CategoryCode>
                    <CategoryCode>18.01.19</CategoryCode>
                    <CategoryCode>18.01.19</CategoryCode>
                    <CategoryCode>18.01.19</CategoryCode>
                    <CategoryCode>18.01.19</CategoryCode>
                    <CategoryCode>18.01.19</CategoryCode>
                    <CategoryCode>18.01.20</CategoryCode>
                    <CategoryCode>18.01.20</CategoryCode>
                    <CategoryCode>18.01.20</CategoryCode>
                    <CategoryCode>18.01.20</CategoryCode>
                    <CategoryCode>18.01.20</CategoryCode>
                    <CategoryCode>18.01.21</CategoryCode>
                    <CategoryCode>18.01.21</CategoryCode>
                    <CategoryCode>18.01.21</CategoryCode>
                    <CategoryCode>18.01.21</CategoryCode>
                    <CategoryCode>18.01.21</CategoryCode>
                    <CategoryCode>18.01.23</CategoryCode>
                    <CategoryCode>18.01.23</CategoryCode>
                    <CategoryCode>18.01.23</CategoryCode>
                    <CategoryCode>18.01.23</CategoryCode>
                    <CategoryCode>18.01.23</CategoryCode>
                    <CategoryCode>18.01.25</CategoryCode>
                    <CategoryCode>18.01.25</CategoryCode>
                    <CategoryCode>18.01.25</CategoryCode>
                    <CategoryCode>18.01.25</CategoryCode>
                    <CategoryCode>18.01.25</CategoryCode>
                    <CategoryCode>27.05.01</CategoryCode>
                    <CategoryCode>27.05.01</CategoryCode>
                    <CategoryCode>27.05.01</CategoryCode>
                    <CategoryCode>27.05.01</CategoryCode>
                    <CategoryCode>27.05.01</CategoryCode>
                    <CategoryCode>27.05.02</CategoryCode>
                    <CategoryCode>27.05.02</CategoryCode>
                    <CategoryCode>27.05.02</CategoryCode>
                    <CategoryCode>27.05.02</CategoryCode>
                    <CategoryCode>27.05.02</CategoryCode>
                    <CategoryCode>27.05.03</CategoryCode>
                    <CategoryCode>27.05.03</CategoryCode>
                    <CategoryCode>27.05.03</CategoryCode>
                    <CategoryCode>27.05.03</CategoryCode>
                    <CategoryCode>27.05.03</CategoryCode>
                    <CategoryCode>27.05.04</CategoryCode>
                    <CategoryCode>27.05.04</CategoryCode>
                    <CategoryCode>27.05.04</CategoryCode>
                    <CategoryCode>27.05.04</CategoryCode>
                    <CategoryCode>27.05.04</CategoryCode>
                    <CategoryCode>27.05.05</CategoryCode>
                    <CategoryCode>27.05.05</CategoryCode>
                    <CategoryCode>27.05.05</CategoryCode>
                    <CategoryCode>27.05.05</CategoryCode>
                    <CategoryCode>27.05.05</CategoryCode>
                    <CategoryCode>27.05.06</CategoryCode>
                    <CategoryCode>27.05.06</CategoryCode>
                    <CategoryCode>27.05.06</CategoryCode>
                    <CategoryCode>27.05.06</CategoryCode>
                    <CategoryCode>27.05.06</CategoryCode>
                    <CategoryCode>27.05.07</CategoryCode>
                    <CategoryCode>27.05.07</CategoryCode>
                    <CategoryCode>27.05.07</CategoryCode>
                    <CategoryCode>27.05.07</CategoryCode>
                    <CategoryCode>27.05.07</CategoryCode>
                    <CategoryCode>27.05.08</CategoryCode>
                    <CategoryCode>27.05.08</CategoryCode>
                    <CategoryCode>27.05.08</CategoryCode>
                    <CategoryCode>27.05.08</CategoryCode>
                    <CategoryCode>27.05.08</CategoryCode>
                    <CategoryCode>27.05.09</CategoryCode>
                    <CategoryCode>27.05.09</CategoryCode>
                    <CategoryCode>27.05.09</CategoryCode>
                    <CategoryCode>27.05.09</CategoryCode>
                    <CategoryCode>27.05.09</CategoryCode>
                    <CategoryCode>27.05.10</CategoryCode>
                    <CategoryCode>27.05.10</CategoryCode>
                    <CategoryCode>27.05.10</CategoryCode>
                    <CategoryCode>27.05.10</CategoryCode>
                    <CategoryCode>27.05.10</CategoryCode>
                    <CategoryCode>27.05.11</CategoryCode>
                    <CategoryCode>27.05.11</CategoryCode>
                    <CategoryCode>27.05.11</CategoryCode>
                    <CategoryCode>27.05.11</CategoryCode>
                    <CategoryCode>27.05.11</CategoryCode>
                    <CategoryCode>27.05.12</CategoryCode>
                    <CategoryCode>27.05.12</CategoryCode>
                    <CategoryCode>27.05.12</CategoryCode>
                    <CategoryCode>27.05.12</CategoryCode>
                    <CategoryCode>27.05.12</CategoryCode>
                    <CategoryCode>27.05.13</CategoryCode>
                    <CategoryCode>27.05.13</CategoryCode>
                    <CategoryCode>27.05.13</CategoryCode>
                    <CategoryCode>27.05.13</CategoryCode>
                    <CategoryCode>27.05.13</CategoryCode>
                    <CategoryCode>27.05.14</CategoryCode>
                    <CategoryCode>27.05.14</CategoryCode>
                    <CategoryCode>27.05.14</CategoryCode>
                    <CategoryCode>27.05.14</CategoryCode>
                    <CategoryCode>27.05.14</CategoryCode>
                    <CategoryCode>27.05.15</CategoryCode>
                    <CategoryCode>27.05.15</CategoryCode>
                    <CategoryCode>27.05.15</CategoryCode>
                    <CategoryCode>27.05.15</CategoryCode>
                    <CategoryCode>27.05.15</CategoryCode>
                    <CategoryCode>27.05.17</CategoryCode>
                    <CategoryCode>27.05.17</CategoryCode>
                    <CategoryCode>27.05.17</CategoryCode>
                    <CategoryCode>27.05.17</CategoryCode>
                    <CategoryCode>27.05.17</CategoryCode>
                    <CategoryCode>27.05.19</CategoryCode>
                    <CategoryCode>27.05.19</CategoryCode>
                    <CategoryCode>27.05.19</CategoryCode>
                    <CategoryCode>27.05.19</CategoryCode>
                    <CategoryCode>27.05.19</CategoryCode>
                    <CategoryCode>27.05.21</CategoryCode>
                    <CategoryCode>27.05.21</CategoryCode>
                    <CategoryCode>27.05.21</CategoryCode>
                    <CategoryCode>27.05.21</CategoryCode>
                    <CategoryCode>27.05.21</CategoryCode>
                    <CategoryCode>27.05.22</CategoryCode>
                    <CategoryCode>27.05.22</CategoryCode>
                    <CategoryCode>27.05.22</CategoryCode>
                    <CategoryCode>27.05.22</CategoryCode>
                    <CategoryCode>27.05.22</CategoryCode>
                    <CategoryCode>27.05.23</CategoryCode>
                    <CategoryCode>27.05.23</CategoryCode>
                    <CategoryCode>27.05.23</CategoryCode>
                    <CategoryCode>27.05.23</CategoryCode>
                    <CategoryCode>27.05.23</CategoryCode>
                    <CategoryCode>27.05.24</CategoryCode>
                    <CategoryCode>27.05.24</CategoryCode>
                    <CategoryCode>27.05.24</CategoryCode>
                    <CategoryCode>27.05.24</CategoryCode>
                    <CategoryCode>27.05.24</CategoryCode>
                    <CategoryCode>27.05.25</CategoryCode>
                    <CategoryCode>27.05.25</CategoryCode>
                    <CategoryCode>27.05.25</CategoryCode>
                    <CategoryCode>27.05.25</CategoryCode>
                    <CategoryCode>27.05.25</CategoryCode>
                    <CategoryCode>29.01.01</CategoryCode>
                    <CategoryCode>29.01.01</CategoryCode>
                    <CategoryCode>29.01.01</CategoryCode>
                    <CategoryCode>29.01.01</CategoryCode>
                    <CategoryCode>29.01.01</CategoryCode>
                    <CategoryCode>29.01.02</CategoryCode>
                    <CategoryCode>29.01.02</CategoryCode>
                    <CategoryCode>29.01.02</CategoryCode>
                    <CategoryCode>29.01.02</CategoryCode>
                    <CategoryCode>29.01.02</CategoryCode>
                    <CategoryCode>29.01.03</CategoryCode>
                    <CategoryCode>29.01.03</CategoryCode>
                    <CategoryCode>29.01.03</CategoryCode>
                    <CategoryCode>29.01.03</CategoryCode>
                    <CategoryCode>29.01.03</CategoryCode>
                    <CategoryCode>29.01.04</CategoryCode>
                    <CategoryCode>29.01.04</CategoryCode>
                    <CategoryCode>29.01.04</CategoryCode>
                    <CategoryCode>29.01.04</CategoryCode>
                    <CategoryCode>29.01.04</CategoryCode>
                    <CategoryCode>29.01.05</CategoryCode>
                    <CategoryCode>29.01.05</CategoryCode>
                    <CategoryCode>29.01.05</CategoryCode>
                    <CategoryCode>29.01.05</CategoryCode>
                    <CategoryCode>29.01.05</CategoryCode>
                    <CategoryCode>29.01.06</CategoryCode>
                    <CategoryCode>29.01.06</CategoryCode>
                    <CategoryCode>29.01.06</CategoryCode>
                    <CategoryCode>29.01.06</CategoryCode>
                    <CategoryCode>29.01.06</CategoryCode>
                    <CategoryCode>29.01.07</CategoryCode>
                    <CategoryCode>29.01.07</CategoryCode>
                    <CategoryCode>29.01.07</CategoryCode>
                    <CategoryCode>29.01.07</CategoryCode>
                    <CategoryCode>29.01.07</CategoryCode>
                    <CategoryCode>29.01.08</CategoryCode>
                    <CategoryCode>29.01.08</CategoryCode>
                    <CategoryCode>29.01.08</CategoryCode>
                    <CategoryCode>29.01.08</CategoryCode>
                    <CategoryCode>29.01.08</CategoryCode>
                    <CategoryCode>29.01.11</CategoryCode>
                    <CategoryCode>29.01.11</CategoryCode>
                    <CategoryCode>29.01.11</CategoryCode>
                    <CategoryCode>29.01.11</CategoryCode>
                    <CategoryCode>29.01.11</CategoryCode>
                    <CategoryCode>29.01.12</CategoryCode>
                    <CategoryCode>29.01.12</CategoryCode>
                    <CategoryCode>29.01.12</CategoryCode>
                    <CategoryCode>29.01.12</CategoryCode>
                    <CategoryCode>29.01.12</CategoryCode>
                    <CategoryCode>29.01.13</CategoryCode>
                    <CategoryCode>29.01.13</CategoryCode>
                    <CategoryCode>29.01.13</CategoryCode>
                    <CategoryCode>29.01.13</CategoryCode>
                    <CategoryCode>29.01.13</CategoryCode>
                    <CategoryCode>29.01.14</CategoryCode>
                    <CategoryCode>29.01.14</CategoryCode>
                    <CategoryCode>29.01.14</CategoryCode>
                    <CategoryCode>29.01.14</CategoryCode>
                    <CategoryCode>29.01.14</CategoryCode>
                    <CategoryCode>29.01.15</CategoryCode>
                    <CategoryCode>29.01.15</CategoryCode>
                    <CategoryCode>29.01.15</CategoryCode>
                    <CategoryCode>29.01.15</CategoryCode>
                    <CategoryCode>29.01.15</CategoryCode>
                  </CategoryCodeDetails>
                </MarkImageCategory>
              </MarkImage>
            </MarkImageDetails>
            <GoodsServicesDetails>
              <GoodsServices>
                <ClassDescriptionDetails>
                  <ClassDescription>
                    <ClassNumber>9</ClassNumber>
                    <GoodsServicesDescription languageCode="ro">Aparate şi instrumente ştiinţifice, nautice, geodezice, fotografice, cinematografice, optice, de cântărire, de măsurare, de semnalizare, de control (verificare), de siguranţă (salvare) şi didactice;aparate şi instrumente pentru conducerea, distribuirea, transformarea, acumularea, reglarea sau comanda curentului electric;aparate pentru înregistrarea, transmiterea, reproducerea sunetelor sau imaginilor;suporţi de înregistrare magnetici, discuri acustice;distribuitoare automate şi mecanisme pentru aparate cu preplată;case înregistratoare, maşini de calculat, echipamente pentru tratarea informaţiei şi calculatoare;extinctoare.</GoodsServicesDescription>
                  </ClassDescription>
                  <ClassDescription>
                    <ClassNumber>16</ClassNumber>
                    <GoodsServicesDescription languageCode="ro">Hârtie, carton şi produse din aceste materiale, necuprinse în alte clase;produse de imprimerie;articole pentru legătorie;fotografii;papetărie;adezivi (materiale colante) pentru papetărie sau menaj;materiale pentru artişti;pensule;maşini de scris şi articole de birou (cu excepţia mobilelor);materiale de instruire sau învăţământ (cu excepţia aparatelor);materiale plastice pentru ambalaj (necuprinse în alte clase);caractere tipografice;clişee.</GoodsServicesDescription>
                  </ClassDescription>
                  <ClassDescription>
                    <ClassNumber>25</ClassNumber>
                    <GoodsServicesDescription languageCode="ro">Îmbrăcăminte, încălţăminte, articole care servesc la acoperirea capului.</GoodsServicesDescription>
                  </ClassDescription>
                  <ClassDescription>
                    <ClassNumber>28</ClassNumber>
                    <GoodsServicesDescription languageCode="ro">Jocuri, jucării;articole de gimnastică şi de sport necuprinse în alte clase;decoraţiuni (ornamente) pentru pomul de Crăciun.</GoodsServicesDescription>
                  </ClassDescription>
                  <ClassDescription>
                    <ClassNumber>35</ClassNumber>
                    <GoodsServicesDescription languageCode="ro">Import, vânzare en gros şi cu amănuntul, regruparea în avantajul terţilor a produselor de îmbrăcăminte şi încălţăminte, accesoriilor de pescuit, vânătoare şi camping, armelor şi muniţiilor de vânătoare şi autoapărare, arcuri şi arbalete, bricege, cuţite şi macete, produselor din piele şi înlocuitori de piele, şepci, pălării şi căşti, produselor de camuflaj, emblemelor şi brelocurilor, echipamentelor şi produselor de autoapărare, ceasuri, ochelari, ambarcaţiuni şi accesorii, binocluri, produse şi accesorii paintball, permiţând consumatorilor să le vadă şi să le cumpere comod, servicii de publicitate, marketing, prezentarea produselor prin toate mijloacele de comunicare pentru vânzare cu amănuntul, publicitate prin radio si televiziune, închiriere de material publicitar, înciriere de spaţii publicitare, închiriere de timp publicitar în mijloacele de comunicare, organizare de expoziţii şi târguri în scopuri comerciale sau publicitare, distribuire de prospecte direct sau prin poştă, administraţie comercială, lucrări de birou.</GoodsServicesDescription>
                  </ClassDescription>
                  <ClassDescription>
                    <ClassNumber>42</ClassNumber>
                    <GoodsServicesDescription languageCode="ro">Servicii ştiinţifice şi tehnologice, precum şi servicii de cercetare şi de creaţie, referitoare la acestea;servicii de analiză şi cercetare industrială;crearea şi dezvoltarea calculatoarelor şi a programelor de calculator.</GoodsServicesDescription>
                  </ClassDescription>
                </ClassDescriptionDetails>
              </GoodsServices>
            </GoodsServicesDetails>
            <SeniorityDetails/>
            <ApplicantDetails>
              <ApplicantKey>
                <Identifier>132789</Identifier>
                <URI>http://bd.osim.ro/trademark/applicant/132789</URI>
              </ApplicantKey>
              <Applicant>
                <ApplicantIdentifier>132789</ApplicantIdentifier>
                <ApplicantLegalEntity>Legal entity</ApplicantLegalEntity>
                <ApplicantAddressBook>
                  <FormattedNameAddress>
                    <Name>
                      <FormattedName>
                        <LastName>AG CAMO INTERNATIONAL S.R.L.</LastName>
                        <OrganizationName>AG CAMO INTERNATIONAL S.R.L.</OrganizationName>
                      </FormattedName>
                    </Name>
                    <Address>
                      <AddressCountryCode>RO</AddressCountryCode>
                      <FormattedAddress>
                        <AddressStreet>Str. Piscul Crăsani nr. 43A, sector 6</AddressStreet>
                        <AddressCity>BUCUREŞTI</AddressCity>
                        <AddressCounty/>
                      </FormattedAddress>
                    </Address>
                  </FormattedNameAddress>
                </ApplicantAddressBook>
              </Applicant>
            </ApplicantDetails>
            <RepresentativeDetails>
              <RepresentativeKey>
                <Identifier>1698</Identifier>
                <URI>http://bd.osim.ro/trademark/representative/1698</URI>
              </RepresentativeKey>
              <Representative>
                <RepresentativeIdentifier>1698</RepresentativeIdentifier>
                <RepresentativeLegalEntity>Legal Entity</RepresentativeLegalEntity>
                <RepresentativeAddressBook>
                  <FormattedNameAddress>
                    <Name>
                      <FormattedName>
                        <LastName>INTELLEXIS SRL</LastName>
                      </FormattedName>
                    </Name>
                    <Address>
                      <AddressCountryCode>RO</AddressCountryCode>
                      <FormattedAddress>
                        <AddressStreet>Str. Cuţitul de Argint nr. 68, et. 2, ap. 4, sector 4</AddressStreet>
                        <AddressCity>BUCUREŞTI</AddressCity>
                        <AddressPostcode>040558</AddressPostcode>
                      </FormattedAddress>
                    </Address>
                  </FormattedNameAddress>
                </RepresentativeAddressBook>
              </Representative>
            </RepresentativeDetails>
          </TradeMark>
        </TradeMarkDetails>
      </TransactionData>
    </TransactionContentDetails>
  </TradeMarkTransactionBody>
</Transaction>
'''


class MockStreamReader:

    def __init__(self):
        self.counter = 0

    def read(self):
        return xml_content.encode('UTF-8')

    def close(self):
        pass


stream_reader = MockStreamReader()


def mock_download(*args, **kwargs):
    return stream_reader


class TestCleanup(unittest.TestCase):

    path_test = os.path.join(os.path.dirname(__file__), 'foo')
    cfg = {
        'step_class': 'pypers.steps.fetch.extract.ro.trademarks.Trademarks',
        'sys_path': None,
        'name': 'trademarks',
        'meta': {
            'job': {},
            'pipeline': {
                'input': {

                },
                'run_id': 1,
                'log_dir': path_test
            },
            'step': {}
        },
        'output_dir': path_test,
    }

    extended_cfg = {
        'input_archive': '2020-06-30-RO-DIFF-INDX-0000.zip'
    }

    def mock_zipextract(source, dest):
        xml_dest = os.path.join(dest, '2020-06-30-RO501990000021977.xml')
        with open(xml_dest, 'w') as f:
            f.write(xml_content)

    def setUp(self):
        self.old_download = download.download
        download.download = mock_download
        try:
            shutil.rmtree(self.path_test)
        except Exception as e:
            pass
        os.makedirs(self.path_test)

        fin = self.extended_cfg['input_archive']
        with open(fin, 'w') as f:
            f.write('toto')
        self.cfg = dict_update(self.cfg, self.extended_cfg)

    def tearDown(self):
        download.download = self.old_download
        try:
            shutil.rmtree(self.path_test)
            pass
        except Exception as e:
            pass

    @patch('pypers.utils.utils.zipextract',
           MagicMock(side_effect=mock_zipextract))
    @patch("pypers.core.interfaces.db.get_db", MagicMock(side_effect=mock_db))
    @patch("pypers.core.interfaces.db.get_db_logger", MagicMock(side_effect=mock_logger))
    def test_process(self):
        mockde_db.update(self.cfg)
        step = Trademarks.load_step("test", "test", "step")
        step.process()


if __name__ == "__main__":
    unittest.main()
