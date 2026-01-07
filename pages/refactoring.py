import streamlit as st
import pandas as pd
import re

def parse_ubipharm_txt(txt_content):
    lines = txt_content.splitlines()
    region = None
    data = []

    for line in lines:
        # Détecter la région
        region_match = re.search(r'Pays/R[�e]gion\s+\d+/\w+\s+(.*)', line)
        if region_match:
            region = region_match.group(1).strip()

        # Détecter les lignes produit
        product_match = re.match(r'\s+([A-Z0-9]+)\s+(.+?)\s+([\d/ ]+)\s+([\d ]+)', line)
        if product_match:
            code = product_match.group(1).strip()
            name = product_match.group(2).strip()
            stock_cr = product_match.group(3).strip()
            sales_raw = product_match.group(4).strip()

            # Nettoyer les ventes
            sales = [int(s) if s.isdigit() else 0 for s in sales_raw.split()]
            while len(sales) < 7:
                sales.append(0)

            # Extraire stock et CR
            stock_match = re.match(r'(\d+)?/?\s*(\d+)?', stock_cr)
            stock = int(stock_match.group(1)) if stock_match and stock_match.group(1) else None
            cr = int(stock_match.group(2)) if stock_match and stock_match.group(2) else None

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

    return pd.DataFrame(data)

def run():
    st.header("⚙️ Refactoring des données")
    uploaded_file = st.file_uploader("Upload fichier TXT brut", type="txt")
    if uploaded_file:
        txt_content = uploaded_file.read().decode("utf-8", errors="ignore")
        df = parse_ubipharm_txt(txt_content)
        st.success("✅ Fichier parsé avec succès")
        st.dataframe(df)

        # Export CSV
        csv = df.to_csv(index=False).encode("utf-8")
        st.download_button("📥 Télécharger CSV", csv, "ventes_refactorées.csv", "text/csv")
