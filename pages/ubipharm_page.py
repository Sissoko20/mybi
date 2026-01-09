import streamlit as st
import pandas as pd
from io import BytesIO

from parsers.ubipharm import parse_ubipharm_txt
from components.repartition import (
    repartir_par_communes,
    repartir_par_communes_horizontal,
    region_to_communes
)

st.header("⚙️ Refactoring des données - Ubipharm")
uploaded_file = st.file_uploader("Upload fichier TXT brut (Ubipharm)", type="txt")

if uploaded_file:
    txt_content = uploaded_file.read().decode("utf-8", errors="ignore")
    df = parse_ubipharm_txt(txt_content)

    if df.empty:
        st.warning("Le parsing n’a retourné aucune ligne. Vérifiez le format du fichier TXT.")
    else:
        st.success("✅ Fichier parsé avec succès")

        # Étape 1 : Vue globale
        st.subheader("🌍 Vue globale : tous les produits")
        st.dataframe(df, use_container_width=True)

        # Étape 2 : Sélecteur de colonnes
        st.subheader("🧩 Sélection des colonnes à garder")
        selected_cols = st.multiselect(
            "Choisissez les colonnes à garder",
            options=df.columns.tolist(),
            default=df.columns.tolist()
        )

        # Appliquer filtrage si demandé
        if st.button("Appliquer le filtrage"):
            df = df[selected_cols]
            st.subheader("🗂️ Aperçu des colonnes sélectionnées (vue globale)")
            st.dataframe(df, use_container_width=True)

        # Étape 3 : Répartition par communes (en bas)
        st.subheader("🏘️ Répartition par communes")
        repartition_mode = st.radio(
            "Choisissez le mode de répartition",
            options=["Verticale (lignes)", "Horizontale (colonnes)"],
            index=0
        )

        regions = df["Région"].dropna().unique()
        repartition_results = {}

        for region in regions:
            st.markdown(f"### 📍 {region}")
            region_df = df[df["Région"] == region]
            st.dataframe(region_df, use_container_width=True)

            if region in region_to_communes:
                communes = region_to_communes[region]

                if repartition_mode == "Verticale (lignes)":
                    df_communes = repartir_par_communes(region_df, communes, col="11/25")
                    st.markdown("#### ➗ Répartition verticale du total 11/25 par communes")
                    st.dataframe(df_communes, use_container_width=True)

                else:
                    df_communes = repartir_par_communes_horizontal(region_df, communes, col="11/25")
                    st.markdown("#### ➗ Répartition horizontale du total 11/25 par communes")
                    st.dataframe(df_communes, use_container_width=True)

                repartition_results[region] = df_communes

        # Étape 4 : Export Excel basé sur la répartition choisie
        if st.button("📥 Générer fichier Excel avec la répartition choisie"):
            output = BytesIO()
            with pd.ExcelWriter(output, engine="openpyxl") as writer:
                sheet_names = {}
                for region, df_communes in repartition_results.items():
                    sheet_name = region[:31]
                    if sheet_name in sheet_names:
                        sheet_names[sheet_name] += 1
                        sheet_name = f"{sheet_name}_{sheet_names[sheet_name]}"
                    else:
                        sheet_names[sheet_name] = 1
                    df_communes.to_excel(writer, index=False, sheet_name=sheet_name)
            excel_data = output.getvalue()

            st.download_button(
                label="📥 Télécharger Excel (répartition par communes)",
                data=excel_data,
                file_name="ventes_reparties.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
