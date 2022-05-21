import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import re
from scipy import stats
from scipy.stats import chi2_contingency
from scipy.stats import chi2


def test():
    print("hello world")

# dimension du dataframe


def df_dimension(data):
    """Retourne la dimension du dataFrame

    Keyword arguments:
    data -- le dataFrame
    """
    row_count, col_count = data.shape
    print(
        '\033[1m', f'Le jeu de données contient {row_count} lignes et {col_count} colonnes.', '\033[0m')


def df_dtypes_count(data):
    """Retourne les dtypes du dataFrame ainsi que le décompte.

    Keyword arguments:
    data -- le dataFrame
    """
    print(data.dtypes.value_counts())


def df_columns_breakdown(data):
    """Retourne la liste des colonnes du dataFrame, classées par dtype.

    Keyword arguments:
    data -- le dataFrame
    """
    df_dtypes = data.dtypes.to_frame()
    df_dtypes.reset_index(inplace=True)
    df_dtypes.columns = ["column", "dtype"]
    df_dtypes["dtypes"] = df_dtypes["dtype"].astype("string")
    df_dtypes.drop("dtype", axis=1, inplace=True)
    return df_dtypes.groupby(by=["dtypes", "column"]).count()


def global_nan_percentage(data):
    """Retourne le pourcentage de nan dans le dataFrame

    Keyword arguments:
    data -- le dataFrame
    """
    return ((data.isnull() | data.isna()).sum().sum() * 100 / data.size).round(2)


def global_nan_percentage_graph(data):
    """Retourne graphe représentant le pourcentatge de valeurs manquantes

    Keyword arguments:
    data -- le dataFrame
    """
    fig, ax = plt.subplots(figsize=(5, 5))
    plt.title("Taux de remplissage avant imputation", size=16)

    # Display pie plot
    ax.pie([global_nan_percentage(data), 100 - global_nan_percentage(data)], autopct='%1.2f%%', explode=(0, 0.1), textprops={
        'fontsize': 14, 'color': 'black', 'backgroundcolor': 'w'})
    plt.legend(["Taux de valeurs manquantes", "Taux de remplissage"],
               shadow=True, loc="center", bbox_to_anchor=(.5, 0), ncol=2)

def nan_columns_breakdown(data):
    """Retourne un tableau avec le nombre de NaN et le taux de NaN, par variables.
    data -- le dataFrame
    """
    nan_count = [] 
    nan_percent = []
    for col in data.columns:
        v = data[col].isna().sum().sum()
        nan_count.append(v)
        nan_percent.append(round(v/data.shape[0]*100,2))
    df_nan = pd.DataFrame([nan_count,nan_percent,data.columns]).T
    df_nan.columns=["Nan count","% NaN","variables"]
    df_nan.set_index("variables",inplace=True)
    df_nan.sort_values(by="% NaN", ascending=False, inplace=True)
    display(df_nan)

def delete_nanfilled_cols(data, cutoff=.90, exclude=False, inplace=False):
    """Suppression des colomnes avec un certain seuil de nan

    Keyword arguments:
    data -- le dataFrame
    cutoff -- le pourcentage seuil
    except -- array of variables to keep anyway
    inplace -- suppression "inplace" ou non
    """
    cols_to_delete = data.isna().sum(axis=0) > data.shape[0]*cutoff
    if exclude and len(exclude) > 0:
        for elt in exclude:
            if elt in cols_to_delete:
                cols_to_delete[elt] = False
    print(
        '\033[1m', f'Avec un cutoff à {cutoff*100}% de valeurs manquantes maximum par colonnes, {cols_to_delete.sum()} colonnes {"on été supprimées." if inplace else "devrait être supprimées."} :')
    print('\033[0m')
    print(cols_to_delete.index[cols_to_delete == True].tolist())
    print('')

    remaining_cols = cols_to_delete.index[cols_to_delete == False].tolist()
    print(
        '\033[1m', f'{len(remaining_cols)} colonnes restantes :\n', '\033[0m')
    print(remaining_cols)

    if inplace:
        data.drop(columns=cols_to_delete[cols_to_delete == True].index, inplace=True)
    else:
        df = data.drop(columns=cols_to_delete[cols_to_delete == True].index).copy()
        return df

def df_description(data, col_count=False, return_only=False):
    """Description des variables enrichie de 2 colonnes = nombre de nan et % de nan
    
    Keyword arguments:
    data -- le dataFrame
    col_count -- le nombre de colonnes avant saut de lignes
    """
    if col_count:
        q, mod = divmod(data.shape[1], col_count)
    else:
        q = 0
        col_count = data.shape[1]

    for i in range(0, q+1):
        b_inf = i*col_count
        b_sup = data.shape[1] if i == data.shape[1] // col_count else (
            i+1)*col_count
        desc = data.iloc[:, range(b_inf, b_sup)].describe(include="all")

        nan_count = (data.shape[0] - desc.loc["count"])
        pourcentage_nan = nan_count/data.shape[0]*100
        pourcentage_nan = pourcentage_nan.astype(float)
        pourcentage_nan = pourcentage_nan.round()

        df_nan = pd.DataFrame(
            {"NAN_count": nan_count, "NAN_percentage": pourcentage_nan}).T
        desc = pd.concat([df_nan, desc])
        if return_only:
            return desc
        else:
            display(desc)


def df_find_empty_cols(data, inplace=False):
    """Trouve les colonnes vides et les supprime si demandé.
    
    Keyword arguments:
    data -- le dataFrame
    inplace -- True or False
    """
    df_count = data.count()
    empty_cols = df_count[df_count == 0]
    print(
        '\033[1m', f'{len(empty_cols)} colonnes vides {"ont été supprimées" if inplace else ""} :\n ', '\033[0m')
    print(', '.join(empty_cols.index))
    if inplace:
        data.drop(empty_cols.index, inplace=True, axis=1)


def df_cols_format(data, to_replace, new_str, inplace=False):
    """Formattage des noms de colonnes
    
    Keyword arguments:
    data -- le dataFrame
    to_replace -- string to replace
    new_str -- new string
    """
    # traces des variables à renommer
    cols_to_format = data.columns[data.columns.str.contains(to_replace)]
    print('\033[1m', f'La chaîne \'{to_replace}\' {"a été remplacée par" if inplace else "devrait être remplacée"} \'{new_str}\' dans {len(cols_to_format)} variables :', '\033[0m')
    print(f'\n{",".join(cols_to_format.tolist())}')

    if inplace == True:
        data.columns = data.columns.str.replace(
            to_replace, new_str, regex=True)
    else:
        return data.columns.str.replace(to_replace, new_str, regex=True)


def df_descriptive_stats(data, features_list=False):
    """ Retourne les statistiques descriptives d'un dataFrame

    Args:
        data : le dataFrame
        features_list : list of columns (optional)
    """
    num_variables = []
    cat_variables = []
    if features_list:
        data = data[features_list]
        vtypes = data[features_list].dtypes
    else:
        data = data
        vtypes = data.dtypes
        
    for v, vtype in zip(data, vtypes):
        if vtype == float or vtype == int:
            num_variables.append(v)
        else:
            cat_variables.append(v)
        
    if len(num_variables) > 0:
        df_temp = data[num_variables].describe(include='all')
        df_temp = df_temp.drop(
            ["25%", "50%", "75%", "count"], axis=0, errors='ignore')
        median = df_temp.median(skipna=True, numeric_only=True)
        mode = df_temp.mode(dropna=True, numeric_only=True).iloc[0, :]
        skew = df_temp.skew(skipna=True, numeric_only=True)
        kurtosis = df_temp.kurtosis(skipna=True, numeric_only=True)

        df_temp = df_temp.T
        df_temp["median"] = median
        df_temp["mode"] = mode
        df_temp["skew"] = skew
        df_temp["kurtosis"] = kurtosis

        df_temp = df_temp.T
        display(df_temp)
        
    if len(cat_variables) > 0:
        df_temp = data[cat_variables].describe(include='all')
        display(df_temp)


def df_outlier_boxplot(series, title, borne_inf, borne_sup, outlier_inf=False, outlier_sup=False):
    """ Retourne un boxplot orienté vers la recherche d'outliers avec des bornes inf et sup et des cutoff inf et sup

    Args:
        series (series): la colonne
        title (string): le titre
        borne_inf (int): la borne inférieure du graphique
        borne_sup (int): la borne supérieure du graphique
        outlier_inf (int): le cutoff inférieur pour les outliers (déssine une ligne rouge)
        outlier_sup (int): le cutoff supérieur pour les outliers (déssine une ligne rouge)
    """
    # Visualisation des outliers
    sns.boxplot(y=series, palette="Set2")

    if outlier_sup is not False:
        plt.annotate("Max : " + str(outlier_sup),
                     xy=(0, outlier_sup), xycoords='data',
                     xytext=(-50, -50), textcoords='offset points',
                     arrowprops=dict(facecolor='k', shrink=0.05),
                     horizontalalignment='right', verticalalignment='bottom')
        plt.axhline(y=outlier_sup, color='r', linestyle='--',
                    label=outlier_sup, linewidth=3)

    if outlier_inf is not False:
        plt.annotate("Min : " + str(outlier_inf),
                     xy=(0, outlier_inf), xycoords='data',
                     xytext=(50, 50), textcoords='offset points',
                     arrowprops=dict(facecolor='k', shrink=0.05),
                     horizontalalignment='left', verticalalignment='bottom')
        plt.axhline(y=outlier_inf, color='b', linestyle='--',
                    label=outlier_inf, linewidth=3)

    plt.title(title)
    plt.ylim([borne_inf, borne_sup])
    plt.show()


def df_outlier_count(data, col, outlier_inf, outlier_sup):
    """ Retourne le nombre d'outliers en fonction d'une borne inférieure et d'une borne supérieure

    Args:
        data (dataframe): le dataFrame
        col (string): la colonne à traiter
        outlier_inf (int): la borne inférieure
        outlier_sup (int): la borne supérieure
    """
    outlier_count = data[(data[col] > outlier_sup) | (
        data[col] < outlier_inf)].count().sum()
    if outlier_count > 0:
        print(f"\033[1m{outlier_count} outliers\033[0m inférieurs à \033[1m{outlier_inf}\033[0m ou supérieurs à \033[1m{outlier_sup}\033[0m")
    else:
        print(f"\033[1m Pas de valeurs aberrantes.\033[0m")


def df_convert_categorical_variables(data):
    """ Pour un variable dont la modalité est inférieure à l'effectif divisé par 2, on peut l'assimiler à une variable catégorielle
    
    Args:
        data (dataframe): le dataFrame
    """
    for col in data.columns.values:
        if data[col].dtype == 'object':
            # print(dataframe[col].unique())
            print(col, ' a été converti en type "Category"')
            if len(data[col].unique()) / len(data[col]) < 0.5:
                data[col] = data[col].astype('category')


def df_plot_distribution(data, feature, xlim=False, ylim=False, boxlim=False):
    """ Retourne une présentation statistiques de la distribution d'une feature avec un barplot, un boxplot et une 
    courbe cumulative des fréquences
    
    Args:
        data (dataframe): le dataFrame
        feature (string): la feature
        xlim (tuple): limite-range axe x du displot 
        ylim (tuple): limite-range axe x du displot 
        blim (tuple): limite-range axe x du boxplot 
    """
    df = data[feature].value_counts(normalize=True).sort_index()

    feat = data[feature]

    print(f"Nombre de valeurs uniques = {len(df)}")
    print(f"Minimum = {feat.min():.2f}")
    print(f"Maximum = {feat.max():.2f}")
    print(f"Moyenne = {feat.mean():.2f}")
    print(f"Médiane = {feat.median():.2f}")
    print(f"Deviation standard = {feat.std():.2f}")
    print(f"Mesure d'asymétrie de la distribution = {feat.skew():.2f}")
    print(f"Mesure d'aplatissement de la distribution = {feat.kurtosis():.2f}")

    fig, (ax1, ax2) = plt.subplots(nrows=1, ncols=2, figsize=(14, 5))
    medianprops = {'color': "black"}
    meanprops = {'marker': 'o', 'markeredgecolor': 'black',
                 'markerfacecolor': 'firebrick'}
    flierprops = {"color": "black", "markeredgecolor": "black"}

    ax3 = ax1.twinx()
    ax1.bar(df.index, df.values)

    ax3.plot(df.index, df.values.cumsum(), linestyle='--',
             marker='o', color='red', label="fréquence cumulée")
    ax3.legend(loc='center right', shadow=True, fontsize='medium')

    ax1.set_xlabel(feature)
    ax1.set_ylabel("Fréquence")

    if xlim:
        ax1.set_xlim(xlim)
    if ylim:
        ax1.set_ylim(ylim)

    bplot1 = ax2.boxplot(data[pd.notnull(feat)][feature], vert=True, labels=[feature],
                         medianprops=medianprops, patch_artist=True, showmeans=True,
                         meanprops=meanprops, flierprops=flierprops)

    bplot1['boxes'][0].set_facecolor("lightsalmon")

    if boxlim:
        ax2.set_ylim(boxlim)

    for ax in [ax1, ax2]:
        ax.yaxis.grid(True)

    fig.tight_layout()
    plt.subplots_adjust(wspace=0.3)
    plt.show()

    #Normality:


def shapiro_test(data, feature):
    """ Retourne une présentation des tests de normalité de Shapiro
    
    Args:
        data (dataframe): le dataFrame
        feature (string): la feature
    """
    a = 0.05
    test = stats.shapiro(data[feature])
    if test.pvalue <= 0.05:
        return f'La distribution de \033[1m{feature}\033[0m s\'éloigne significativement de la loi Normale. , W= {round(test.statistic,2)}, P value= {round(test.pvalue,2)}\n'
    else:
        return f"La distribution de {feature} \033[4m\033[1ms'approche de la loi normale\033[0m, W= {round(test.statistic,2)}, P value= {round(test.pvalue,2)}.\n"


def df_chisquared_table(data, feature1, feature2, alpha: float, displayTable=False):
    """ Retourne une présentation des tests de normalité de Shapiro
    
    Args:
        data (dataframe): le dataFrame
        feature1 (string): la feature #1
        feature2 (string): la feature #2
        alpha (float): le taux alpha souhaité
    """
    df_cross = pd.crosstab(data[feature1], data[feature2])

    if displayTable:
        print('Tableau de contingence :')
        display(df_cross)

    stat_chi2, p, dof, expected_table = chi2_contingency(df_cross.values)

    prob = 1.0-alpha
    valeur_critique = chi2.ppf(prob, dof)
    print('Probabilité = %.3f,\nValeur critique = %.3f,\np-value = %.3f,\nValeur chi2 = %.3f\n' %
          (prob, valeur_critique, p, stat_chi2))
    if abs(stat_chi2) >= valeur_critique or p <= alpha:
        print('H0 rejetée : il y a dépendance.')
    else:
        print('H0 maintenue : il n\'y a pas de dépendance')

####################################################
#                                                  #
#               FROM OpenClassrooms                #
#                                                  #
####################################################


def display_circles(pcs, n_comp, pca, axis_ranks, labels=None, label_rotation=0, lims=None):
    for d1, d2 in axis_ranks:  # On affiche les 3 premiers plans factoriels, donc les 6 premières composantes
        if d2 < n_comp:

            # initialisation de la figure
            fig, ax = plt.subplots(figsize=(10, 10))
            # détermination des limites du graphique
            if lims is not None:
                xmin, xmax, ymin, ymax = lims
            elif pcs.shape[1] < 30:
                xmin, xmax, ymin, ymax = -1, 1, -1, 1
            else:
                xmin, xmax, ymin, ymax = min(pcs[d1, :]), max(
                    pcs[d1, :]), min(pcs[d2, :]), max(pcs[d2, :])

            # affichage des flèches
            # s'il y a plus de 30 flèches, on n'affiche pas le triangle à leur extrémité
            if pcs.shape[1] < 30:
                plt.quiver(np.zeros(pcs.shape[1]), np.zeros(pcs.shape[1]),
                           pcs[d1, :], pcs[d2, :],
                           angles='xy', scale_units='xy', scale=1, color="grey")
                # (voir la doc : https://matplotlib.org/api/_as_gen/matplotlib.pyplot.quiver.html)
            else:
                lines = [[[0, 0], [x, y]] for x, y in pcs[[d1, d2]].T]
                ax.add_collection(LineCollection(
                    lines, axes=ax, alpha=.1, color='black'))

            # affichage des noms des variables
            if labels is not None:
                for i, (x, y) in enumerate(pcs[[d1, d2]].T):
                    if x >= xmin and x <= xmax and y >= ymin and y <= ymax:
                        plt.text(x, y, labels[i], fontsize='14', ha='center',
                                 va='center', rotation=label_rotation, color="blue", alpha=0.5)

            # affichage du cercle
            circle = plt.Circle((0, 0), 1, facecolor='none', edgecolor='b')
            plt.gca().add_artist(circle)

            # définition des limites du graphique
            plt.xlim(xmin, xmax)
            plt.ylim(ymin, ymax)

            # affichage des lignes horizontales et verticales
            plt.plot([-1, 1], [0, 0], color='grey', ls='--')
            plt.plot([0, 0], [-1, 1], color='grey', ls='--')

            # nom des axes, avec le pourcentage d'inertie expliqué
            plt.xlabel('F{} ({}%)'.format(
                d1+1, round(100*pca.explained_variance_ratio_[d1], 1)))
            plt.ylabel('F{} ({}%)'.format(
                d2+1, round(100*pca.explained_variance_ratio_[d2], 1)))

            plt.title("Cercle des corrélations (F{} et F{})".format(d1+1, d2+1))
            plt.show(block=False)
####################################################
#                                                  #
#               FROM OpenClassrooms                #
#                                                  #
####################################################


def display_factorial_planes(X_projected, n_comp, pca, axis_ranks, labels=None, alpha=1, illustrative_var=None):
    for d1, d2 in axis_ranks:
        if d2 < n_comp:

            # initialisation de la figure
            fig = plt.figure(figsize=(7, 6))

            # affichage des points
            if illustrative_var is None:
                plt.scatter(X_projected[:, d1],
                            X_projected[:, d2], alpha=alpha)
            else:
                illustrative_var = np.array(illustrative_var)
                for value in np.unique(illustrative_var):
                    selected = np.where(illustrative_var == value)
                    plt.scatter(
                        X_projected[selected, d1], X_projected[selected, d2], alpha=alpha, label=value)
                plt.legend()

            # affichage des labels des points
            if labels is not None:
                for i, (x, y) in enumerate(X_projected[:, [d1, d2]]):
                    plt.text(x, y, labels[i],
                             fontsize='14', ha='center', va='center')

            # détermination des limites du graphique
            boundary = np.max(np.abs(X_projected[:, [d1, d2]])) * 1.1
            plt.xlim([-boundary, boundary])
            plt.ylim([-boundary, boundary])

            # affichage des lignes horizontales et verticales
            plt.plot([-100, 100], [0, 0], color='grey', ls='--')
            plt.plot([0, 0], [-100, 100], color='grey', ls='--')

            # nom des axes, avec le pourcentage d'inertie expliqué
            plt.xlabel('F{} ({}%)'.format(
                d1+1, round(100*pca.explained_variance_ratio_[d1], 1)))
            plt.ylabel('F{} ({}%)'.format(
                d2+1, round(100*pca.explained_variance_ratio_[d2], 1)))

            plt.title(
                "Projection des individus (sur F{} et F{})".format(d1+1, d2+1))
            plt.show(block=False)
####################################################
#                                                  #
#               FROM OpenClassrooms                #
#                                                  #
####################################################


def display_scree_plot(pca):
    scree = pca.explained_variance_ratio_*100
    plt.bar(np.arange(len(scree))+1, scree)
    plt.plot(np.arange(len(scree))+1, scree.cumsum(), c="red", marker='o')
    plt.xlabel("rang de l'axe d'inertie")
    plt.ylabel("pourcentage d'inertie")
    plt.title("Eboulis des valeurs propres")
    plt.show(block=False)
####################################################
#                                                  #
#               FROM OpenClassrooms                #
#                                                  #
####################################################


def eta_squared(x, y):
    moyenne_y = y.mean()
    classes = []
    for classe in x.unique():
        yi_classe = y[x == classe]
        classes.append({'ni': len(yi_classe),
                        'moyenne_classe': yi_classe.mean()})
    SCT = sum([(yj-moyenne_y)**2 for yj in y])
    SCE = sum([c['ni']*(c['moyenne_classe']-moyenne_y)**2 for c in classes])
    return SCE/SCT
