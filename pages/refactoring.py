import streamlit as st
import pandas as pd
import re

def parse_ubipharm_txt(txt_content):
    lines = txt_content.splitlines()
    region = None
    data = []
    totals = []

    for line in lines:
        # Détecter la région
        region_match = re.search(r'Pays.*R.gion\s+\d+/\w+\s+(.*)', line)
        if region_match:
            region = region_match.group(1).strip()

        # Détecter les lignes produit
        product_match = re.match(
            r'\s+([A-Z0-9]+)\s+(.+?)\s+([\d/ ]+)\s+(\d+)?\s*(\d+)?\s*(\d+)?\s*(\d+)?\s*(\d+)?\s*(\d+)?\s*(\d+)?',
            line
        )
        if product_match and region:
            code = product_match.group(1).strip()
            name = product_match.group(2).strip()
            stock_cr = product_match.group(3).strip()

            # Stock / CR
            stock_match = re.match(r'(\d+)?\s*/\s*(\d+)?', stock_cr)
            stock = int(stock_match.group(1)) if stock_match and stock_match.group(1) else None
            cr = int(stock_match.group(2)) if stock_match and stock_match.group(2) else None

            # Ventes
            sales = []
            for i in range(4, 11):
                val = product_match.group(i)
                sales.append(int(val) if val and val.isdigit() else 0)

            data.append({
                "Région": region,
                "Code Produit": code,
                "Nom Produit": name,
                "Stock": stock,
                "CR": cr,
                "11/25": sales[0],
                "M-1": sales[1],
                "M-2": sales[2],
                "M-3": sales[3],
                "M-4": sales[4],
                "M-5": sales[5],
                "M-6": sales[6],
            })

        # Détecter la ligne de total pays/région
        total_match = re.match(r'Total\s+pays.*r.gion\s+(\d+)?\s*/\s*(\d+)?', line, re.IGNORECASE)
        if total_match and region:
            stock_total = int(total_match.group(1)) if total_match.group(1) else None
            cr_total = int(total_match.group(2)) if total_match.group(2) else None
            totals.append({
                "Région": region,
                "Stock Total": stock_total,
                "CR Total": cr_total
            })

    return pd.DataFrame(data), pd.DataFrame(totals)

# --- Page Refactoring ---
st.header("⚙️ Refactoring des données")
uploaded_file = st.file_uploader("Upload fichier TXT brut", type="txt")

if uploaded_file:
    txt_content = uploaded_file.read().decode("utf-8", errors="ignore")
    df_products, df_totals = parse_ubipharm_txt(txt_content)

    if df_products.empty:
        st.warning("Le parsing n’a retourné aucune ligne. Vérifiez le format du fichier TXT.")
    else:
        st.success("✅ Fichier parsé avec succès")

        # Vue globale produits
        st.subheader("🌍 Vue globale : tous les produits")
        st.dataframe(df_products, use_container_width=True)

        # Vue par région
        st.subheader("📋 Produits regroupés par région")
        regions = df_products["Région"].dropna().unique()
        for region in regions:
            st.markdown(f"### 📍 {region}")
            region_df = df_products[df_products["Région"] == region]
            st.dataframe(region_df, use_container_width=True)

        # Totaux par région
        if not df_totals.empty:
            st.subheader("📊 Totaux par région (ligne 'Total pays/région')")
            st.dataframe(df_totals, use_container_width=True)
