import streamlit as st
import pandas as pd
import plotly.express as px
from streamlit_option_menu import option_menu
from numerize.numerize import numerize
import time
from streamlit_extras.metric_cards import style_metric_cards
import plotly.graph_objs as go

#uncomment this line if you use mysql
#from query import *

st.set_page_config(page_title="Dashboard",page_icon="🟡",layout="wide")
st.header("🌐Analytical Processing, KPI, Trends & Predictions")

#all graphs we use custom css not streamlit
theme_plotly = None


# load Style css
with open('style.css')as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html = True)

#uncomment these two lines if you fetch data from mysql
#result = view_all_data()
#df=pd.DataFrame(result,columns=["Policy","Expiry","Location","State","Region","Investment","Construction","BusinessType","Earthquake","Flood","Rating","id"])

#load excel file | comment this line when  you fetch data from mysql
df=pd.read_excel('data.xlsx', sheet_name='Sheet1')


st.sidebar.image("data/logo9.png",caption="Online Analytics")

#switcher
st.sidebar.header("Please Filter")
region=st.sidebar.multiselect(
    "SELECT REGION",
     options=df["Region"].unique(),
     default=df["Region"].unique(),
)
location=st.sidebar.multiselect(
    "SELECT LOCATION",
     options=df["Location"].unique(),
     default=df["Location"].unique(),
)
construction=st.sidebar.multiselect(
    "SELECT CONSTRUCTION",
     options=df["Construction"].unique(),
     default=df["Construction"].unique(),
)

df_selection=df.query(
    "Region==@region & Location==@location & Construction ==@construction"
)


#this function performs basic descriptive analytics like Mean,Mode,Sum  etc
def Home():
    with st.expander("Tabular"):
        showData=st.multiselect('Filter: ',df_selection.columns,default=[])
        st.write(df_selection[showData])
#compute top analytics
total_investment = float(df_selection['Investment'].sum())
investment_mode = float(df_selection['Investment'].mode())
investment_mean = float(df_selection['Investment'].mean())
investment_median = float(df_selection['Investment'].median())
rating = float(df_selection['Rating'].sum())

total1,total2,total3,total4,total5=st.columns(5,gap='large')
with total1:
    st.info('Total Investment',icon="💲")
    st.metric(label="Sum TZS", value=f"{total_investment:,.0f}")

with total2:         
    st.info('Most Frequent',icon="💲")
    st.metric(label="Mode TZS",value=f"{investment_mode:,.0f}")

with total3:
    st.info('Average',icon="💲")
    st.metric(label="Average TZS",value=f"{investment_mean:,.0f}")

with total4:
    st.info('Central Earnings',icon="💲")
    st.metric(label="Median TZS",value=f"{investment_median:,.0f}")

with total5:
    st.info('Ratings',icon="💲")
    st.metric(label="Rating",value=numerize(rating),help=f""" Total Rating: {rating} """)
style_metric_cards(background_color="#1f252b",border_left_color="#d16f0d",border_color="#d16f0d",box_shadow="#F71938")


#graphs
def graphs():
    investment_by_business_type=(
        df_selection.groupby(by=["BusinessType"]).count()[["Investment"]].sort_values(by="Investment")
    )
    
    fig_investment=px.bar(
       investment_by_business_type,
       x="Investment",
       y=investment_by_business_type.index,
       orientation="h",
       title="<b> Investment By Business Type </b>",
       color_discrete_sequence=["#5451f0"]*len(investment_by_business_type),
       template="plotly_white",
    )
    fig_investment.update_layout(
     plot_bgcolor="rgba(0,0,0,0)",
     font=dict(color="black"),
     yaxis=dict(showgrid=False),  # Show y-axis grid and set its color  
     paper_bgcolor='rgba(0, 0, 0, 0)',  # Set paper background color to transparent
     xaxis=dict(showgrid=False)  # Show x-axis grid and set its color
     )

    #simple line graph investment by state
    investment_state=df_selection.groupby(by=["State"]).count()[["Investment"]]
    fig_state=px.line(
       investment_state,
       x=investment_state.index,
       y="Investment",
       orientation="v",
       title="<b> Investment By State </b>",
       color_discrete_sequence=["#5451f0"]*len(investment_state),
       template="plotly_white",
    )
    fig_state.update_layout(
    xaxis=dict(tickmode="linear"),
    plot_bgcolor="rgba(0,0,0,0)",
    yaxis=(dict(showgrid=False))
     )

    left,right=st.columns(2)
    left.plotly_chart(fig_state,use_container_width=True)
    right.plotly_chart(fig_investment,use_container_width=True)
    
#function to show current earnings against expected target
def Progressbar():
    st.markdown("""<style>.stProgress > div > div > div > div { background-image: linear-gradient(to right, #99ff99 , #FFFF00)}</style>""",unsafe_allow_html=True,)
    target=3000000000
    current=df_selection["Investment"].sum()
    percent=round((current/target*100))
    mybar=st.progress(0)

    if percent>100:
     st.subheader("Target Done !")
    else:
     st.write("you have ",percent, "% " ,"of ", (format(target, 'd')), "TZS")
    for percent_complete in range(percent):
     time.sleep(0.1)
     mybar.progress(percent_complete+1,text=" Target Percentage")

#menu bar
def sideBar():
 with st.sidebar:
    selected=option_menu(
    menu_title="Main Menu",
    options=["Home","Progress"],
    icons=["house","eye"],
    menu_icon="cast",
    default_index=0
)
 if selected == "Home":
    st.subheader(f"Page: {selected}")
    Home()
    graphs()
 if selected == "Progress":
    st.subheader(f"Page: {selected}")
    Progressbar()
    graphs()

sideBar()

st.subheader('Pick Features To Explore Distributions Trends By Quartiles',)
#feature_x = st.selectbox('Select feature for x Qualitative data', df_selection.select_dtypes("object").columns)
feature_y = st.selectbox('Select feature for y Quantitative Data', df_selection.select_dtypes("number").columns)
fig2 = go.Figure(
    data=[go.Box(x=df['BusinessType'], y=df[feature_y])],
    layout=go.Layout(
        title=go.layout.Title(text="Business Type By Quartiles Of Investment"),
        plot_bgcolor='rgba(0, 0, 0, 0)',  # Set plot background color to transparent
        paper_bgcolor='rgba(0, 0, 0, 0)',  # Set paper background color to transparent
        xaxis=dict(showgrid=True, gridcolor='#1f252b'),  # Show x-axis grid and set its color
        yaxis=dict(showgrid=True, gridcolor='#1f252b'),  # Show y-axis grid and set its color
        font=dict(color='#cecdcd'),  # Set text color to black
    )
)
# Display the Plotly figure using Streamlit
st.plotly_chart(fig2,use_container_width=True)

#theme
hide_st_style="""

<style>
#MainMenu {visibility:hidden;}
footer {visibility:hidden;}
header {visibility:hidden;}
</style>
"""