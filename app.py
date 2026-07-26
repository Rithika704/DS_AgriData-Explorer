"""
AgriData Explorer - Interactive Streamlit Dashboard
Run with: streamlit run app.py
"""

import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="AgriData Explorer", layout="wide", page_icon="🌾")

# ---------------------------------------------------------------
# Load data
# ---------------------------------------------------------------
@st.cache_data
def load_data():
    df = pd.read_csv("ICRISAT_cleaned.csv")
    df["TOTAL MILLET PRODUCTION"] = (
        df["PEARL MILLET PRODUCTION (1000 tons)"].fillna(0)
        + df["FINGER MILLET PRODUCTION (1000 tons)"].fillna(0)
    )
    return df

df = load_data()

st.title("🌾 AgriData Explorer")
st.caption("Understanding Indian Agriculture — Crop Production, Yield & Area (1966–2017)")

# ---------------------------------------------------------------
# Sidebar filters
# ---------------------------------------------------------------
st.sidebar.header("Filters")

all_states = sorted(df["State Name"].unique())
selected_states = st.sidebar.multiselect("State(s)", all_states, default=all_states)

year_min, year_max = int(df["Year"].min()), int(df["Year"].max())
year_range = st.sidebar.slider("Year range", year_min, year_max, (year_min, year_max))

crop_options = ["RICE", "WHEAT", "SUGARCANE", "SUNFLOWER", "GROUNDNUT", "SOYABEAN",
                "OILSEEDS", "COTTON", "SORGHUM"]
selected_crop = st.sidebar.selectbox("Crop (for trend tab)", crop_options)

# apply filters
mask = (
    df["State Name"].isin(selected_states)
    & df["Year"].between(year_range[0], year_range[1])
)
fdf = df[mask]

st.sidebar.markdown("---")
st.sidebar.metric("Rows in current selection", f"{len(fdf):,}")

# ---------------------------------------------------------------
# Tabs mirroring the 15 EDA points from the project brief
# ---------------------------------------------------------------
tab1, tab2, tab3, tab4, tab5 = st.tabs(
    ["📊 Top Producers", "📈 Trends Over Time", "🗺️ District Deep-Dive",
     "🌻 Crop Comparisons", "🧮 Area vs Production"]
)

# --- TAB 1: Top Producers -----------------------------------------------
with tab1:
    col1, col2 = st.columns(2)

    with col1:
        rice_state = fdf.groupby("State Name")["RICE PRODUCTION (1000 tons)"].sum().sort_values(ascending=False).head(7)
        fig = px.bar(rice_state, orientation="h", title="Top 7 States - Rice Production",
                     labels={"value": "Rice Production (1000 tons)", "State Name": "State"})
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        wheat_state = fdf.groupby("State Name")["WHEAT PRODUCTION (1000 tons)"].sum().sort_values(ascending=False).head(5)
        fig = px.pie(values=wheat_state.values, names=wheat_state.index,
                     title="Top 5 Wheat Producing States (Share %)")
        st.plotly_chart(fig, use_container_width=True)

    col3, col4 = st.columns(2)
    with col3:
        oil_state = fdf.groupby("State Name")["OILSEEDS PRODUCTION (1000 tons)"].sum().sort_values(ascending=False).head(5)
        fig = px.bar(oil_state, orientation="h", title="Oilseed Production - Top 5 States")
        st.plotly_chart(fig, use_container_width=True)

    with col4:
        sun_state = fdf.groupby("State Name")["SUNFLOWER PRODUCTION (1000 tons)"].sum().sort_values(ascending=False).head(7)
        fig = px.bar(sun_state, orientation="h", title="Top 7 States - Sunflower Production")
        st.plotly_chart(fig, use_container_width=True)

    col5, col6 = st.columns(2)
    with col5:
        groundnut_state = fdf.groupby("State Name")["GROUNDNUT PRODUCTION (1000 tons)"].sum().sort_values(ascending=False).head(7)
        fig = px.bar(groundnut_state, orientation="h", title="Top 7 States - Groundnut Production")
        st.plotly_chart(fig, use_container_width=True)

    with col6:
        oil_major = fdf.groupby("State Name")["OILSEEDS PRODUCTION (1000 tons)"].sum().sort_values(ascending=False).head(10)
        fig = px.bar(oil_major, orientation="h", title="Oilseed Production - Major States (Top 10)")
        st.plotly_chart(fig, use_container_width=True)

# --- TAB 2: Trends Over Time --------------------------------------------
with tab2:
    sugarcane_year = fdf.groupby("Year")["SUGARCANE PRODUCTION (1000 tons)"].sum()
    fig = px.line(sugarcane_year, title="India's Sugarcane Production Over Time")
    st.plotly_chart(fig, use_container_width=True)

    rw_year = fdf.groupby("Year")[["RICE PRODUCTION (1000 tons)", "WHEAT PRODUCTION (1000 tons)"]].sum()
    fig = px.line(rw_year, title="Rice vs Wheat Production Over Time")
    st.plotly_chart(fig, use_container_width=True)

    millet_year = fdf.groupby("Year")["TOTAL MILLET PRODUCTION"].sum()
    fig = px.line(millet_year, title="Millet Production Over Time (Pearl + Finger Millet)")
    st.plotly_chart(fig, use_container_width=True)

    # Generic crop trend based on sidebar selection
    prod_col = f"{selected_crop} PRODUCTION (1000 tons)"
    if prod_col in fdf.columns:
        crop_year = fdf.groupby("Year")[prod_col].sum()
        fig = px.line(crop_year, title=f"{selected_crop.title()} Production Trend (Selected Crop)")
        st.plotly_chart(fig, use_container_width=True)

# --- TAB 3: District Deep-Dive ------------------------------------------
with tab3:
    st.subheader("Rice Production by West Bengal Districts")
    wb_rice = fdf[fdf["State Name"] == "West Bengal"].groupby("Dist Name")["RICE PRODUCTION (1000 tons)"].sum().sort_values(ascending=False)
    if len(wb_rice):
        fig = px.bar(wb_rice, orientation="h", title="Rice Production by District - West Bengal")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("West Bengal not in current state filter selection.")

    st.subheader("Top 10 Wheat Production Years - Uttar Pradesh")
    up_wheat = fdf[fdf["State Name"] == "Uttar Pradesh"].groupby("Year")["WHEAT PRODUCTION (1000 tons)"].sum().sort_values(ascending=False).head(10)
    if len(up_wheat):
        fig = px.bar(up_wheat, title="Top 10 Wheat Years - Uttar Pradesh")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Uttar Pradesh not in current state filter selection.")

# --- TAB 4: Crop Comparisons ---------------------------------------------
with tab4:
    st.subheader("Kharif vs Rabi Sorghum Production by State")
    sorghum_state = fdf.groupby("State Name")[["KHARIF SORGHUM PRODUCTION (1000 tons)", "RABI SORGHUM PRODUCTION (1000 tons)"]].sum()
    sorghum_state = sorghum_state[(sorghum_state.T != 0).any()].sort_values("KHARIF SORGHUM PRODUCTION (1000 tons)", ascending=False).head(10)
    fig = px.bar(sorghum_state, barmode="group", title="Kharif vs Rabi Sorghum - Top 10 States")
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("Soybean: Top 5 States by Production & Yield Efficiency")
    soy = fdf.groupby("State Name").agg(
        Production=("SOYABEAN PRODUCTION (1000 tons)", "sum"),
        Yield=("SOYABEAN YIELD (Kg per ha)", "mean")
    ).sort_values("Production", ascending=False).head(5).reset_index()
    fig = px.bar(soy, x="State Name", y="Production", title="Soybean Production - Top 5 States")
    st.plotly_chart(fig, use_container_width=True)
    fig2 = px.line(soy, x="State Name", y="Yield", markers=True, title="Soybean Avg Yield - Top 5 States")
    st.plotly_chart(fig2, use_container_width=True)

    st.subheader("Rice vs Wheat Yield Across States")
    yield_compare = fdf.groupby("State Name")[["RICE YIELD (Kg per ha)", "WHEAT YIELD (Kg per ha)"]].mean().dropna(how="all")
    yield_compare = yield_compare.sort_values("RICE YIELD (Kg per ha)", ascending=False)
    fig = px.bar(yield_compare, barmode="group", title="Average Rice vs Wheat Yield by State")
    st.plotly_chart(fig, use_container_width=True)

# --- TAB 5: Area vs Production --------------------------------------------
with tab5:
    st.subheader("Impact of Area Cultivated on Production")
    crop_choice = st.radio("Choose crop", ["RICE", "WHEAT", "MAIZE"], horizontal=True)
    area_col = f"{crop_choice} AREA (1000 ha)"
    prod_col = f"{crop_choice} PRODUCTION (1000 tons)"
    scatter_df = fdf[[area_col, prod_col, "State Name", "Year"]].dropna()
    fig = px.scatter(scatter_df, x=area_col, y=prod_col, color="State Name",
                      hover_data=["Year"], title=f"{crop_choice.title()}: Area vs Production",
                      opacity=0.5)
    st.plotly_chart(fig, use_container_width=True)

st.markdown("---")
st.caption("AgriData Explorer | GUVI Capstone Project | Data Source: ICRISAT District-Level Data")
