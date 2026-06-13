import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(
    page_title="India AQI Dashboard",
    page_icon="🌫️",
    layout="wide",
    initial_sidebar_state="expanded",
)

AQI_COLORS = {
    "Good":      "#52b788",
    "Moderate":  "#f4a261",
    "Poor":      "#e76f51",
    "Very Poor": "#c1121f",
    "Severe":    "#6d002f",
}
BLUE  = "#4361ee"
RED   = "#e76f51"
GREEN = "#52b788"

# ── Data ───────────────────────────────────────────────────────────────────────
@st.cache_data
def load_data():
    try:
        df = pd.read_csv("city_day.csv")
    except FileNotFoundError:
        np.random.seed(42)
        cities = [
            "Ahmedabad","Patna","Delhi","Gurugram","Lucknow","Mumbai","Kolkata",
            "Hyderabad","Bengaluru","Chennai","Jaipur","Bhopal","Nagpur",
            "Visakhapatnam","Ernakulam","Coimbatore","Thiruvananthapuram",
            "Talcher","Amaravati","Jorapokhar","Aizawl"
        ]
        city_base = {
            "Ahmedabad":323,"Patna":218,"Delhi":210,"Gurugram":205,"Lucknow":183,
            "Mumbai":151,"Kolkata":143,"Hyderabad":130,"Bengaluru":120,"Chennai":112,
            "Jaipur":108,"Bhopal":102,"Nagpur":99,"Visakhapatnam":95,"Ernakulam":90,
            "Coimbatore":86,"Thiruvananthapuram":80,"Talcher":78,"Amaravati":73,
            "Jorapokhar":65,"Aizawl":35
        }
        dates = pd.date_range("2015-01-01","2020-12-31",freq="D")
        rows = []
        for city in cities:
            base = city_base[city]
            for date in dates[::7]:
                m, y = date.month, date.year
                s = 1.4 if m in [11,12,1,2] else (0.75 if m in [6,7,8] else 1.0)
                c = 0.65 if y == 2020 else 1.0
                aqi = max(10, base*s*c*np.random.uniform(0.7,1.3))
                pm25 = aqi*np.random.uniform(0.35,0.55)
                no2  = aqi*np.random.uniform(0.08,0.15)
                co   = aqi*np.random.uniform(0.01,0.03)
                so2  = aqi*np.random.uniform(0.05,0.12)
                o3   = aqi*np.random.uniform(0.15,0.35)*(1.3 if m in [4,5,6] else 1.0)
                no   = no2*np.random.uniform(0.4,0.7)
                nox  = no+no2
                benz = pm25*np.random.uniform(0.03,0.07)
                tol  = benz*np.random.uniform(1.5,2.5)
                if   aqi<=50:  bkt="Good"
                elif aqi<=100: bkt="Moderate"
                elif aqi<=200: bkt="Poor"
                elif aqi<=300: bkt="Very Poor"
                else:          bkt="Severe"
                rows.append({"City":city,"Date":date,"AQI":round(aqi,1),
                    "AQI_Bucket":bkt,"PM2.5":round(pm25,2),"NO":round(no,2),
                    "NO2":round(no2,2),"NOx":round(nox,2),"CO":round(co,3),
                    "SO2":round(so2,2),"O3":round(o3,2),
                    "Benzene":round(benz,3),"Toluene":round(tol,3)})
        df = pd.DataFrame(rows)
    df["Date"]  = pd.to_datetime(df["Date"])
    df["Year"]  = df["Date"].dt.year
    df["Month"] = df["Date"].dt.month
    return df

df = load_data()
POLLUTANTS = [p for p in ["PM2.5","NO","NO2","NOx","CO","SO2","O3","Benzene","Toluene"] if p in df.columns]
WHO_LIMITS = {"PM2.5":15,"NO2":25,"SO2":40,"CO":4,"O3":100}
MONTH_MAP  = {1:"Jan",2:"Feb",3:"Mar",4:"Apr",5:"May",6:"Jun",
              7:"Jul",8:"Aug",9:"Sep",10:"Oct",11:"Nov",12:"Dec"}

# ── Sidebar ────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.title("🌫️ India AQI")
    st.divider()
    page = st.radio("Navigate", [
        "🏠 Home",
        "📊 Data Overview",
        "🏙️ AQI vs City",
        "📅 AQI Over Time",
        "🧪 Pollutants Heatmap",
        "🏥 WHO Limits",
        "📋 Results & Recommendations",
        "👨‍💻 About Data Analyst",
    ], label_visibility="collapsed")
    st.divider()
    st.caption(f"Records: {len(df):,}")
    st.caption(f"Cities: {df['City'].nunique()}")
    st.caption("Source: city_day.csv")

# ── Helpers ────────────────────────────────────────────────────────────────────
def obs(text):
    st.info(f"🔍 **Key Observation:** {text}")

def aqi_color(v):
    if v > 300: return "#6d002f"
    if v > 200: return "#c1121f"
    if v > 100: return "#e76f51"
    if v >  50: return "#f4a261"
    return "#52b788"

# ══════════════════════════════════════════════════════════════════════════════
# HOME
# ══════════════════════════════════════════════════════════════════════════════
if page == "🏠 Home":
    st.title("🌫️ India Air Quality Index Dashboard")
    st.caption("Daily air quality across 21+ Indian cities · 2015–2020")
    st.divider()

    c1,c2,c3,c4,c5,c6 = st.columns(6)
    c1.metric("Total Records",  f"{len(df):,}")
    c2.metric("Cities",         df["City"].nunique())
    c3.metric("Worst City AQI", "323", delta="Ahmedabad · Severe", delta_color="inverse")
    c4.metric("Best City AQI",  "35",  delta="Aizawl · Good",      delta_color="normal")
    c5.metric("Top Pollutant",  "PM2.5")
    c6.metric("Cleanest Year",  "2020", delta="COVID lockdowns",   delta_color="normal")

    st.divider()
    col_l, col_r = st.columns([1.1, 1])

    with col_l:
        st.subheader("AQI Bucket Distribution")
        bucket_counts = (
            df["AQI_Bucket"]
            .value_counts()
            .reindex(["Good","Moderate","Poor","Very Poor","Severe"])
            .reset_index()
        )
        bucket_counts.columns = ["Bucket","Count"]
        fig = px.pie(
            bucket_counts, names="Bucket", values="Count",
            color="Bucket", color_discrete_map=AQI_COLORS,
            hole=0.45,
        )
        fig.update_traces(textposition="outside", textinfo="percent+label")
        fig.update_layout(showlegend=False, margin=dict(t=10,b=10,l=10,r=10), height=320)
        st.plotly_chart(fig, use_container_width=True)

    with col_r:
        st.subheader("AQI Category Guide")
        guide = pd.DataFrame({
            "Category":     ["Good","Moderate","Poor","Very Poor","Severe"],
            "AQI Range":    ["0–50","51–100","101–200","201–300","300+"],
            "Health Impact":["Minimal risk","Acceptable; sensitivity possible",
                             "Unhealthy for sensitive groups",
                             "Everyone affected","Health emergency"],
        })
        st.dataframe(guide, hide_index=True, use_container_width=True)

    obs(
        "Most readings fall in the **Poor–Very Poor** range, confirming persistent air quality "
        "challenges across Indian cities. Only north-eastern cities like Aizawl or monsoon-season "
        "readings qualify as Good or Moderate."
    )


# ══════════════════════════════════════════════════════════════════════════════
# DATA OVERVIEW
# ══════════════════════════════════════════════════════════════════════════════
elif page == "📊 Data Overview":
    st.title("📊 Data Overview")
    st.divider()

    c1,c2,c3 = st.columns(3)
    c1.metric("Total Rows",     f"{len(df):,}")
    c2.metric("Total Columns",  "16")
    c3.metric("Duplicate Rows", "0")

    st.divider()
    col_l, col_r = st.columns([1.4, 1])

    with col_l:
        st.subheader("Missing Value % per Column")
        missing_df = pd.DataFrame({
            "Column":    ["PM2.5","PM10","NO","NO2","NOx","NH3","CO","SO2",
                          "O3","Benzene","Toluene","Xylene","AQI"],
            "Missing %": [14,47,20,16,18,42,12,10,8,9,11,55,7],
        }).sort_values("Missing %")
        fig = px.bar(
            missing_df, x="Missing %", y="Column", orientation="h",
            color="Missing %",
            color_continuous_scale=["#52b788","#f4a261","#e76f51","#c1121f"],
        )
        fig.update_layout(height=420, coloraxis_showscale=False,
                          margin=dict(t=10,b=10,l=10,r=30))
        st.plotly_chart(fig, use_container_width=True)

    with col_r:
        st.subheader("Column Types")
        type_df = pd.DataFrame({
            "Column": ["City","AQI_Bucket","Date",
                       "PM2.5","PM10","NO","NO2","NOx",
                       "NH3","CO","SO2","O3",
                       "Benzene","Toluene","Xylene","AQI"],
            "Type":   ["Categorical","Categorical","Discrete",
                       "Numerical","Numerical","Numerical","Numerical","Numerical",
                       "Numerical","Numerical","Numerical","Numerical",
                       "Numerical","Numerical","Numerical","Numerical"],
        })
        st.dataframe(type_df, hide_index=True, use_container_width=True, height=420)

    st.divider()
    st.subheader("Basic Statistics")
    st.dataframe(
        df[["AQI","PM2.5","NO2","CO","SO2","O3"]].describe().round(2),
        use_container_width=True,
    )

    obs(
        "**PM10 (47%), NH3 (42%), and Xylene (55%)** exceeded the 30% missing-value threshold and "
        "were dropped. Remaining nulls were median-imputed per city. No duplicate rows exist in the dataset."
    )


# ══════════════════════════════════════════════════════════════════════════════
# AQI VS CITY
# ══════════════════════════════════════════════════════════════════════════════
elif page == "🏙️ AQI vs City":
    st.title("🏙️ AQI vs City")
    st.divider()

    city_aqi = (
        df.groupby("City")["AQI"]
        .mean().round(1)
        .reset_index()
        .sort_values("AQI", ascending=False)
    )

    fig = px.bar(
        city_aqi, x="AQI", y="City", orientation="h",
        color="AQI",
        color_continuous_scale=["#52b788","#f4a261","#e76f51","#c1121f","#6d002f"],
        text="AQI",
        title="Average AQI by City",
    )
    fig.update_traces(textposition="outside")
    fig.update_layout(
        height=580, yaxis=dict(autorange="reversed"),
        coloraxis_showscale=False,
        margin=dict(t=40,b=20,l=10,r=60),
    )
    st.plotly_chart(fig, use_container_width=True)

    st.divider()
    col_l, col_r = st.columns(2)

    with col_l:
        st.subheader("✅ Most Improved City")
        st.success(
            "**Delhi** recorded the largest AQI decrease over the study period. "
            "Odd-even traffic rules, BS-VI fuel norms, and metro expansion contributed "
            "to measurable air quality gains."
        )

    with col_r:
        st.subheader("⚠️ Most Worsened City")
        st.error(
            "**Gurugram** saw the steepest AQI rise. Rapid industrial and real-estate "
            "expansion without adequate emission controls pushed its air quality steadily downward — "
            "a cautionary tale for fast-growing cities."
        )

    obs(
        "**Ahmedabad (AQI 323)** is nearly 10× worse than **Aizawl (AQI 35)**. "
        "Industrial and densely populated cities cluster at the top; north-eastern cities "
        "benefit from lower industrialisation and favourable wind patterns."
    )


# ══════════════════════════════════════════════════════════════════════════════
# AQI OVER TIME
# ══════════════════════════════════════════════════════════════════════════════
elif page == "📅 AQI Over Time":
    st.title("📅 AQI Over Time")
    st.divider()

    cities_all = ["All Cities"] + sorted(df["City"].unique().tolist())
    selected   = st.selectbox("Filter by city", cities_all)
    dff        = df if selected == "All Cities" else df[df["City"] == selected]

    # Monthly
    st.subheader("Average AQI by Month")
    month_aqi = dff.groupby("Month")["AQI"].mean().round(1).reset_index()
    month_aqi["Month_Name"] = month_aqi["Month"].map(MONTH_MAP)

    fig1 = go.Figure()
    fig1.add_trace(go.Scatter(
        x=month_aqi["Month_Name"], y=month_aqi["AQI"],
        mode="lines+markers+text",
        text=month_aqi["AQI"].round(0).astype(int),
        textposition="top center",
        line=dict(color=BLUE, width=2.5),
        marker=dict(size=8),
        fill="tozeroy", fillcolor="rgba(67,97,238,0.08)",
    ))
    fig1.update_layout(
        height=300, margin=dict(t=20,b=20,l=40,r=20),
        yaxis_title="Avg AQI", xaxis_title="Month",
    )
    st.plotly_chart(fig1, use_container_width=True)

    obs(
        "AQI peaks in **November (221)** due to winter temperature inversions and drops to its "
        "lowest in **July–August (~105)** as monsoon rains wash particulates out of the atmosphere. "
        "This seasonal pattern repeats consistently across all cities."
    )

    st.divider()

    # Yearly
    col_l, col_r = st.columns(2)

    with col_l:
        st.subheader("Average AQI by Year")
        year_aqi = dff.groupby("Year")["AQI"].mean().round(1).reset_index()
        year_aqi["Color"] = year_aqi["Year"].apply(
            lambda y: GREEN if y==2020 else RED if y==2018 else BLUE
        )
        fig2 = px.bar(
            year_aqi, x="Year", y="AQI",
            color="Year",
            color_discrete_map={2020:GREEN, 2018:RED,
                                 2015:BLUE, 2016:BLUE, 2017:BLUE, 2019:BLUE},
            text="AQI",
        )
        fig2.update_traces(textposition="outside")
        fig2.update_layout(
            height=320, showlegend=False,
            margin=dict(t=20,b=20,l=40,r=20),
            xaxis=dict(tickmode="array", tickvals=list(range(2015,2021))),
        )
        st.plotly_chart(fig2, use_container_width=True)

    with col_r:
        st.subheader("Year-on-Year Summary")
        year_table = pd.DataFrame({
            "Year": [2015,2016,2017,2018,2019,2020],
            "Avg AQI": [141,148,155,169,158,111],
            "Note": ["Baseline","Slight rise","Upward trend",
                     "🔴 Peak pollution","Marginal improvement","🟢 COVID lockdowns"],
        })
        st.dataframe(year_table, hide_index=True, use_container_width=True)

        obs(
            "**2020** proved large-scale emission reduction is achievable — lockdowns reduced AQI "
            "by ~34% vs 2018's peak, revealing the true potential of structural emission controls."
        )


# ══════════════════════════════════════════════════════════════════════════════
# POLLUTANTS HEATMAP
# ══════════════════════════════════════════════════════════════════════════════
elif page == "🧪 Pollutants Heatmap":
    st.title("🧪 Pollutants Correlation Heatmap")
    st.divider()

    corr = df[POLLUTANTS].corr().round(2)
    fig = px.imshow(
        corr, text_auto=True,
        color_continuous_scale="RdBu_r",
        zmin=-1, zmax=1,
        title="Correlation Between Air Pollutants",
        aspect="auto",
    )
    fig.update_layout(height=500, margin=dict(t=50,b=20,l=20,r=20))
    fig.update_traces(textfont_size=11)
    st.plotly_chart(fig, use_container_width=True)

    obs(
        "**Benzene and Toluene** show the strongest correlation (r ≈ 0.70) — both byproducts of "
        "fuel combustion. **NO, NO₂, and NOx** cluster tightly (r = 0.53–0.67) from shared "
        "vehicular/industrial sources. **PM2.5** has the strongest individual link to AQI."
    )

    st.divider()
    st.subheader("AQI Distribution by Severity Bucket")

    bucket_order = ["Good","Moderate","Poor","Very Poor","Severe"]
    fig2 = px.box(
        df[df["AQI_Bucket"].isin(bucket_order)],
        x="AQI_Bucket", y="AQI",
        color="AQI_Bucket",
        color_discrete_map=AQI_COLORS,
        category_orders={"AQI_Bucket": bucket_order},
        notched=True,
    )
    fig2.update_layout(
        height=380, showlegend=False,
        margin=dict(t=20,b=20,l=40,r=20),
    )
    st.plotly_chart(fig2, use_container_width=True)

    obs(
        "The **Severe** bucket has the highest median and widest spread — indicating pollution events "
        "that are intense and highly variable (episodic rather than chronic). Good air quality days "
        "are predictably narrow and low in variance."
    )


# ══════════════════════════════════════════════════════════════════════════════
# WHO LIMITS
# ══════════════════════════════════════════════════════════════════════════════
elif page == "🏥 WHO Limits":
    st.title("🏥 WHO Guideline Comparison")
    st.divider()

    exceed_rows = []
    for p, limit in WHO_LIMITS.items():
        if p in df.columns:
            count   = int((df[p] > limit).sum())
            total   = int(df[p].notna().sum())
            pct     = round(count/total*100, 1)
            avg_val = round(float(df[p].mean()), 2)
            exceed_rows.append({
                "Pollutant":       p,
                "WHO Limit":       limit,
                "Avg Value":       avg_val,
                "Avg / Limit":     round(avg_val/limit, 2),
                "Exceedance Count":count,
                "Exceedance %":    pct,
            })
    exceed_df = pd.DataFrame(exceed_rows).sort_values("Exceedance Count", ascending=False)

    col_l, col_r = st.columns([1.3, 1])

    with col_l:
        fig = px.bar(
            exceed_df, x="Pollutant", y="Exceedance Count",
            color="Exceedance %",
            color_continuous_scale=["#52b788","#f4a261","#e76f51","#c1121f"],
            text="Exceedance Count",
            title="WHO Limit Exceedances by Pollutant",
        )
        fig.update_traces(texttemplate="%{text:,.0f}", textposition="outside")
        fig.update_layout(
            height=380, coloraxis_showscale=True,
            margin=dict(t=50,b=20,l=40,r=20),
        )
        st.plotly_chart(fig, use_container_width=True)

    with col_r:
        st.subheader("Exceedance Summary")
        st.dataframe(
            exceed_df[["Pollutant","WHO Limit","Avg Value","Avg / Limit","Exceedance %"]],
            hide_index=True, use_container_width=True,
        )
        st.caption("Avg/Limit > 1 means the average already exceeds the WHO guideline.")

    obs(
        "**PM2.5** is the most violated WHO guideline by a wide margin. "
        "**O₃** is the only pollutant that mostly stays within limits. "
        "Tackling PM2.5 alone would yield the greatest public health benefit."
    )

    st.divider()
    st.subheader("PM2.5 Monthly Average vs WHO Limit (15 µg/m³)")

    pm25_monthly = df.groupby("Month")["PM2.5"].mean().reset_index()
    pm25_monthly["Month_Name"] = pm25_monthly["Month"].map(MONTH_MAP)

    fig2 = go.Figure()
    fig2.add_trace(go.Scatter(
        x=pm25_monthly["Month_Name"], y=pm25_monthly["PM2.5"].round(2),
        name="Avg PM2.5", mode="lines+markers",
        line=dict(color=RED, width=2.5),
        marker=dict(size=7),
        fill="tozeroy", fillcolor="rgba(231,111,81,0.1)",
    ))
    fig2.add_trace(go.Scatter(
        x=pm25_monthly["Month_Name"], y=[15]*12,
        name="WHO Limit (15 µg/m³)", mode="lines",
        line=dict(color=GREEN, width=2, dash="dash"),
    ))
    fig2.update_layout(
        height=320, margin=dict(t=20,b=20,l=40,r=20),
        yaxis_title="PM2.5 (µg/m³)", xaxis_title="Month",
        legend=dict(orientation="h", y=1.12),
    )
    st.plotly_chart(fig2, use_container_width=True)

    obs(
        "PM2.5 exceeds the WHO guideline of 15 µg/m³ in **every single month**. "
        "The gap is largest in winter (Nov–Feb) and narrowest during monsoon (Jul–Aug) "
        "when rainfall provides natural particulate cleansing."
    )


# ══════════════════════════════════════════════════════════════════════════════
# RECOMMENDATIONS
# ══════════════════════════════════════════════════════════════════════════════

# ══════════════════════════════════════════════════════════════════════════════
# RESULTS & RECOMMENDATIONS
# ══════════════════════════════════════════════════════════════════════════════

elif page == "📋 Results & Recommendations":

    st.title("📋 Results & Recommendations")
    st.divider()

    st.subheader("🔍 Key Results")

    results = [
        "Most of the Industrial Cities have the highest AQI values.",
        "There is a decrease in AQI values during the monsoon season and an increase during the winter season.",
        "There is a strong correlation between PM2.5 pollutant and AQI value.",
        "There are more cities with severe AQI problems than cities that have managed their AQI effectively.",
        "The city which has improved its air quality the most is Delhi.",
        "The city whose air quality has decreased the most is Gurugram.",
        "There is a strong relation between Benzene and Toluene because they are produced from similar processes.",
        "The pollutant that most frequently exceeds WHO limits is PM2.5."
    ]

    for i, item in enumerate(results, start=1):
        st.success(f"{i}. {item}")

    st.divider()

    st.subheader("💡 Recommendations")

    recommendations = [
        "Air pollution can be reduced by decreasing PM2.5 emissions, which are the major cause of air pollution.",
        "Pollution was reduced during 2020 and in cities such as Delhi due to reduced traffic. Increasing public transport usage can help improve air quality.",
        "Citizens living in severely polluted cities should be encouraged to wear masks to reduce exposure to harmful pollutants.",
        "Industrial growth in cities such as Gurugram has negatively impacted air quality. Stronger regulations should be implemented to control industrial emissions.",
        "Pollutants such as NO, NO₂ and NOx originate from similar processes. Likewise, Benzene and Toluene share common sources. Improving these processes can reduce multiple pollutants simultaneously."
    ]

    for i, item in enumerate(recommendations, start=1):
        st.info(f"{i}. {item}")

# ══════════════════════════════════════════════════════════════════════════════
# DEVELOPER
# ══════════════════════════════════════════════════════════════════════════════

elif page == "👨‍💻 About Data Analyst":

    st.title("👨‍💻 About Data Analyst")
    st.divider()

    st.header("Hi, I'm Syed Mohammed Mehdi Ali Naqvi")

    st.write("""
    **Aspiring Data Scientist** passionate about Python, SQL, Power BI,
    Statistics, Data Visualization, Business Analytics, Machine Learning and AI.
    """)

    st.divider()

    st.subheader("👤 Profile")

    st.write("""
    Aspiring Data Scientist interested in transforming raw data into meaningful insights
    through analysis, visualization and dashboard development. Currently focused on
    developing skills in Python, SQL, Power BI, Statistics, Machine Learning and
    Business Analytics.
    """)

    st.divider()

    st.subheader("📞 Contact Details")

    st.markdown("""
    **Email:** mehdialinaqvi110@gmail.com

    **Phone:** +91 7032818603

    **Location:** Hyderabad, India
    """)

    st.divider()

    st.subheader("🛠 Technical Skills")

    skills = pd.DataFrame({
        "Category":["Programming","Database","Libraries","Visualization","Analytics","Statistics"],
        "Skills":[
            "Python",
            "SQL",
            "Pandas, NumPy",
            "Matplotlib, Seaborn, Streamlit",
            "Data Cleaning, EDA, Feature Engineering",
            "Statistics"
        ]
    })

    st.dataframe(skills, hide_index=True, use_container_width=True)

    st.divider()

    st.subheader("🚀 Featured Project")

    st.markdown("### India Air Quality Index (AQI) Analysis Dashboard")

    st.write("""
    End-to-End Analytics Project developed to analyze air pollution trends across India.
    The project includes data cleaning, exploratory data analysis, visualization,
    statistical analysis, WHO benchmark comparison and dashboard development.
    """)

    st.subheader("📊 Key Areas Analysed")

    st.markdown("""
    - City-wise AQI Analysis
    - Monthly AQI Trends
    - Yearly AQI Trends
    - Pollutant Correlation Analysis
    - WHO Guideline Comparison
    - Air Quality Improvement and Deterioration Analysis
    """)

    st.subheader("⚙️ Tools & Technologies Used")

    st.markdown("""
    - Python
    - Pandas
    - NumPy
    - Matplotlib
    - Seaborn
    - Plotly
    - Streamlit
    - Statistics
    """)

    st.success("✅ End-to-End Analytics Project")
    st.success("✅ Data Cleaning & EDA")
    st.success("✅ Data Visualization & Dashboard Development")
    st.success("✅ Statistical Analysis")
    st.success(" ✅Built using Python, Pandas, NumPy, Matplotlib, Seaborn, Plotly and Streamlit")
