sync_productes = """
select 
    p.EMPRESA_ID, p.ID, p.ARTICLE, p.CODI_ARTICLE, pa.ID ATRIBUT_ID, 
    p.DATA_BAIXA, pm.PES PES_NET, pm.PES + pm.TARA PES_BRUT, pm.AMPLADA, pm.LLARGADA,
    pm.ALTURA, pe.EAN13_ARTICLE, 1, pe.EAN13_CAIXA, pp.UNITATS_SUP, pl.CONTROL_LOTS_VENDA,
    alf.tip_unitat_logistica_id, alf.unitat_logistica_format_id, alf.unitats_pal
from ARTICLES p
join ARTICLES_ATRIBUTS pa on p.ID = pa.ARTICLE_ID
join ARTICLES_MIDES pm on p.ID = pm.ARTICLE_ID
join ARTICLES_EANS pe on pa.ID = pe.ARTICLE_ATRIBUT_ID
join ARTICLES_PARAMETRES pp on p.ID = pp.ARTICLE_ID
left join ( select article_id,tip_unitat_logistica_id, max(unitat_logistica_format_id) unitat_logistica_format_id,max(unitats_pal) unitats_pal
               from articles_logistica_formats alf
               join tip_unitats_logistiques tu on tu.id = alf.tip_unitat_logistica_id
              where tu.palet = 'S'
               group by article_id,tip_unitat_logistica_id ) alf on alf.article_id = p.id
left join SELECT_ARTICLES_C_ESTOCS(p.ID, CURRENT_DATE) pl on p.ID = pl.ARTICLE_ID
join (select ARTICLE_ATRIBUT_ID, SUM(QUANTITAT_TOTAL) STOCK 
       FROM  ARTICLES_ESTOCS 
       GROUP BY ARTICLE_ATRIBUT_ID 
       HAVING SUM(QUANTITAT_TOTAL) > 0
) ps on pa.ID = ps.ARTICLE_ATRIBUT_ID
where p.ID not in (1268, 2127) and pl.CONTROL_ESTOCS = 'S';
"""

sync_clients = """
select c.EMPRESA_ID, t.ID, c.ID, t.NOM_LLARG_I_COMERCIAL, c.DATA_BAIXA, LEFT(tp.IDIOMA_CODI,2)
from clients c
join tercers t on c.TERCER_ID = t.ID
join tercers_parametres tp on t.id = tp.tercer_id
"""

sync_transportistes = """
select r.EMPRESA_ID, r.ID, t.NOM_LLARG
FROM REPARTIDORS r
join TERCERS t on r.TERCER_ID = t.ID
"""

sync_comanda = """
select
    c.EMPRESA_ID, 
    c.ID COMANDA_ID,
    c.NUMERO_COMANDA,
    c.REFERENCIA,
    cd.TERCER_ID CLIENT_ID,
    cd.REPARTIDOR_ID,
    CASE WHEN c_cli.COMANDA_ID IS NULL THEN cd_ter.NOM_LLARG_I_COMERCIAL ELSE c_cli.TERCER END NOM_CLIENT,
    CASE WHEN c_cli.COMANDA_ID IS NULL THEN cd_carrer.CARRER ELSE c_cli.ADRECA END ADRECA,
    CASE WHEN c_cli.COMANDA_ID IS NULL THEN cd_adr.CPOSTAL ELSE c_cli.CPOSTAL END CPOSTAL,
    CASE WHEN c_cli.COMANDA_ID IS NULL THEN cd_poble.POBLE ELSE c_cli_poble.POBLE END POBLE,
    CASE WHEN c_cli.COMANDA_ID IS NULL THEN cd_comu.PAIS_CODI ELSE c_cli_comu.PAIS_CODI END CODI_PAIS,
    CASE WHEN c_cli.COMANDA_ID IS NULL THEN NULL ELSE c_cli.TELEFON END TELEFON,
    CASE WHEN c_cli.COMANDA_ID IS NULL THEN NULL ELSE c_cli.EMAIL END MAIL,
    cd.PES_NET, cd.PES_BRUT

from comandes c
join comandes_distribucio cd on c.ID = cd.COMANDA_ID
join adreces_distribucio cd_adr on cd.ADRECA_DISTRIBUCIO_ID = cd_adr.ID
join carrers cd_carrer on cd_adr.CARRER_ID = cd_carrer.ID
join pobles cd_poble on cd_adr.POBLE_ID = cd_poble.ID
join comarques cd_coma on cd_poble.COMARCA_ID = cd_coma.ID
join provincies cd_prov on cd_coma.PROVINCIA_ID = cd_prov.ID
join comunitats cd_comu on cd_prov.COMUNITAT_ID = cd_comu.ID

join tercers cd_ter on cd.TERCER_ID = cd_ter.ID
join clients cd_cli on cd_ter.ID = cd_cli.TERCER_ID and c.EMPRESA_ID = cd_cli.EMPRESA_ID    
left join comandes_client c_cli on c.ID = c_cli.COMANDA_ID
left join pobles c_cli_poble on c_cli.POBLE_ID = c_cli_poble.ID
left join comarques c_cli_coma on c_cli_poble.COMARCA_ID = c_cli_coma.ID
left join provincies c_cli_prov on c_cli_coma.PROVINCIA_ID = c_cli_prov.ID
left join comunitats c_cli_comu on c_cli_prov.COMUNITAT_ID = c_cli_comu.ID
where c.ID = ?
"""

sync_comanda_linies = """
select cl_atr.ID ATRIBUT_ID, sum(cl.QUANTITAT) QUANTITAT, min(cl.NUMERO_LINIA) nl, min(cl.DESCRIPCIO), 
sum(cl.QUANTITAT) QUANTITAT_PENDENT
from comandes c
join comandes_linies cl on c.ID = cl.COMANDA_ID
join articles_atributs cl_atr on cl.ARTICLE_ATRIBUT_ID = cl_atr.ID
join articles cl_art on cl_atr.ARTICLE_ID = cl_art.ID
LEFT join select_articles_c_estocs(cl_art.ID, c.DATA_COMANDA) cl_art_stk on cl_art.ID =  cl_art_stk.ARTICLE_ID
where cl_art_stk.CONTROL_ESTOCS = 'S' and c.ID = ?
group by ATRIBUT_ID
HAVING sum(cl.QUANTITAT) > 0
"""

sync_comandes_pendents = """
SELECT C.ID, C.NUMERO_COMANDA, C.DATA_COMANDA,C.DATA_INSERCIO,C.REFERENCIA, T.NOM_LLARG_I_COMERCIAL
FROM COMANDES C
JOIN CLIENTS CL ON C.CLIENT_ID = CL.ID
JOIN TERCERS T ON CL.TERCER_ID = T.ID
JOIN COMANDES_DISTRIBUCIO CD ON C.ID = CD.COMANDA_ID
left join SELECT_COMANDES_ESTATS_MAG(C.ID) CE ON C.ID = CE.COMANDA_ID
where C.DATA_INICI IS NULL 
AND CE.MAG_PENDENT_SERVIR = 'S' 
AND C.DATA_ANULACIO IS NULL
and CD.REPARTIDOR_ID IS NOT NULL ;
"""

sync_magatzems_ordres_pendents = """
SELECT MO.ID,MO.NUMERO_ORDRE, MO.DATA_INSERCIO, MO.MAGATZEM_ORDRE,MO.MAGATZEM_SORTIDA_ID, MO.MAGATZEM_ENTRADA_ID ,MO.OBSERVACIONS, U.NUMERO_UNITAT
FROM MAGATZEMS_ORDRES MO
JOIN MAGATZEMS_ORDRES_DETALL MD ON MO.ID = MD.MAGATZEM_ORDRE_ID
JOIN UNITATS_LOGISTIQUES U ON U.ID = MD.UNITAT_LOGISTICA_ID
where MO.DATA_BLOQUEIG IS null
AND MO.DATA_CONFIRMACIO IS NOT null
AND MO.DATA_FINALITZACIO IS NULL
AND MO.MAGATZEM_ENTRADA_ID = ? ;
"""

sync_moviments_magatzems_pendents = """
select ma.id,ma.magatzem_origen_id,ma.magatzem_desti_id, ma.data_insercio,ma.data_peticio,ma.observacions
from moviments_magatzems ma
where ma.data_lliurament is null
and ma.magatzem_origen_id = ? ;
"""

sync_clients_mrest = """
        select cl.id client_id_client,
        cl.codi_client,
        t.nom_llarg nom_client,
        t.nom_comercial nom_comercial_client,
        t.nif nif_client,

        ga.adreca adreca_client,
        a.cpostal cpostal_client,
        a.poble_id poble_id_client,
        p.poble poble_client,
        pr.id provincia_id_client,
        pr.provincia provincia_client,

        ga2.adreca adreca_client_distibucio,
        a2.cpostal cpostal_client_distibucio,
        a2.poble_id poble_id_client_distibucio,
        p2.poble poble_client_distibucio,
        pr2.id provincia_id_client_distibucio,
        pr2.provincia provincia_client_distibucio,

        cl.data_baixa data_baixa_client,
        cl.descompte descompte_1_client,
        cl.desc_ppago descompte_2_client,
        cl.cond_pag_id cond_pag_id_client,
        clp.recarrec recarrec_client,
        impostos.impost_normal,
        v.empleat_id empleat_id_client,
        cl1.id client_id_destinatari,
        cl1.codi_client codi_client_destinatari,
        t1.nom_llarg nom_destinatari,
        t1.nom_comercial nom_comercial_destinatari,
        t1.nif nif_destinatari,
        cc.desc_seccio,
        cc.cond_pag_seccio,
        ga1.adreca adreca_destinatari,
        a1.cpostal cpostal_destinatari,
        a1.poble_id poble_id_destinatari,
        p1.poble poble_destinatari,
        pr1.id provincia_id_destinatari,
        pr1.provincia provincia_destinatari,
        cl1.data_baixa data_baixa_destinatari,
        cl1.descompte descompte_1_destinatari,
        cl1.desc_ppago descompte_2_destinatari,
        cl1.cond_pag_id cond_pag_id_destinatari,
        clp1.recarrec recarrec_destinatari,
        ct1.empleat_id empleat_id_destinatari,
        v1t.nom_llarg empleat_nom_destinatari,
        vt.nom_llarg empleat_nom_destinatari

        from clients cl
        join clients_parametres clp on cl.id = clp.client_id
        join tercers t on t.id = cl.tercer_id

        join adreces a on t.id = a.tercer_id and a.id = cl.adreca_id
        join pobles p on p.id = a.poble_id
        join comarques co on co.id = p.comarca_id
        join provincies pr on pr.id = co.provincia_id
        join comunitats com on com.id = pr.comunitat_id
        join paisos pa on pa.codi = com.pais_codi
        join tip_adreces ta on ta.id = a.tip_adreca_id

        join adreces a2 on  t.id = a.tercer_id and a2.id = cl.adreca_distri_id
        join pobles p2 on p2.id = a2.poble_id
        join comarques co2 on co2.id = p2.comarca_id
        join provincies pr2 on pr2.id = co2.provincia_id
        join comunitats com2 on com2.id = pr2.comunitat_id
        join paisos pa2 on pa2.codi = com2.pais_codi
        join tip_adreces ta2 on ta2.id = a2.tip_adreca_id

        join cartera_tercers ct on ct.tercer_id = t.id and ct.empresa_id = cl.empresa_id
        join venedors v on v.empleat_id = ct.empleat_id
        join empleats ve on ct.empleat_id = ve.id
        join tercers vt on ve.tercer_id = vt.id

        left join genera_nom_adreca(ta.nom_breu,a.adreca,a.numero,a.escala,a.pis,a.porta) ga on 1 = 1
        left join genera_nom_adreca(ta2.nom_breu,a2.adreca,a2.numero,a2.escala,a2.pis,a2.porta) ga2 on 1 = 1
        left join clients_seccions cc on cc.client_id = cl.id
        left join tercers t1 on t1.id = cc.tercer_id
        left join clients cl1 on t1.id = cl1.tercer_id and cl1.empresa_id = cl.empresa_id
        left join clients_parametres clp1 on cl1.id = clp1.client_id
        left join adreces a1 on a1.id = cl1.adreca_distri_id
        left join pobles p1 on p1.id = a1.poble_id
        left join comarques co1 on co1.id = p1.comarca_id
        left join provincies pr1 on pr1.id = co1.provincia_id
        left join comunitats com1 on com1.id = pr1.comunitat_id
        left join paisos pa1 on pa1.codi = com1.pais_codi
        left join tip_adreces ta1 on ta1.id = a1.tip_adreca_id
        left join genera_nom_adreca(ta1.nom_breu,a1.adreca,a1.numero,a1.escala,a1.pis,a1.porta) ga1 on 1 = 1
        left join cartera_tercers ct1 on ct1.tercer_id = t1.id and ct1.empresa_id = cl1.empresa_id
        left join venedors v1 on v1.empleat_id = ct1.empleat_id
        left join empleats v1e on ct1.empleat_id = v1e.id
        left join tercers v1t on v1e.tercer_id = v1t.id
        left join (
            select ci.client_id,ic.normal impost_normal
            from impostos_clients ic
            join clients_impostos ci on ci.impost_id = ic.id
            where ci.data_activacio = (
                select max(data_activacio)
                from clients_impostos ci2
                where ci2.client_id = ci.client_id
                and ci2.data_activacio <= current_date 
            )
        ) impostos on impostos.client_id = cl.id
        where cl.empresa_id = 1 
        and not exists (
            select null
            from clients_seccions cs
            where cs.empresa_id = cl.empresa_id
            and cs.tercer_id = t.id
        )
        and char_length(t.nif)> 5
        and ( (t1.id is null) or ((t1.id is not null) and (v1.empleat_id is not null)) )
        order by cl.codi_client;

    """
