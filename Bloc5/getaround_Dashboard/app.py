import streamlit as st
import pandas as pd
import plotly.express as px
import os

# Config
st.set_page_config(page_title="GetAround Analysis", page_icon=":racing_car:", layout="wide")
st.markdown(
    """
    <div style="text-align: center;">
        <img src="https://lever-client-logos.s3.amazonaws.com/2bd4cdf9-37f2-497f-9096-c2793296a75f-1568844229943.png" 
             alt="Getaround Logo" width="900">
    </div>
    """,
    unsafe_allow_html=True
)


# Load data
data_path = os.path.join(os.getcwd(), "data", "get_around_delay_analysis.csv")

@st.cache_data
def load_data():
    df = pd.read_csv(data_path)
    return df

df = load_data()
st.header("New feature")
st.write("A car won't be displayed in the search results if the requested checkin or checkout times are too close from an already booked rental to avoid problematic case.")
st.write("We define a problematic case as a rental where the previous driver is late and the time before the next rental is shorter than the delay.")

img_col1, img_col2, img_col3 = st.columns(3)
img_path_1 = os.path.join(os.getcwd(), "data", "ideal_rental.png")
img_path_2 = os.path.join(os.getcwd(), "data", "late_rental.png")
img_path_3 = os.path.join(os.getcwd(), "data", "problematic_rental.png")
with img_col1:
    st.image(img_path_1, use_container_width=True)

with img_col2:
    st.image(img_path_2, use_container_width=True)

with img_col3:
    st.image(img_path_3, use_container_width=True)
st.divider()


st.header("Analysis of implementing the new feature")

# Show dataframe if the check is checked
if st.checkbox("Show raw data"): 
    st.dataframe(df)

df.rename(columns={"delay_at_checkout_in_minutes": "delay", "previous_ended_rental_id": "previous_id", "time_delta_with_previous_rental_in_minutes": "time_delta" }, inplace=True)


# check missing values
data_missing_values = (100 * df.isnull().sum() / df.shape[0]).reset_index()
data_missing_values.columns = ["Column", "Missing Percentage"]
#print(data_missing_values)

# only display columns with missing values
data_missing_values = data_missing_values[data_missing_values["Missing Percentage"] > 0]
fig = px.bar(data_missing_values, 
             x="Column",
             y="Missing Percentage",
             title="Percentage of missing values ​​per column",
             color="Missing Percentage",
             text_auto='.2f',
             )
st.plotly_chart(fig)
st.write("From the graph above, we can see that there are missing values in the column **delay**, **previous_id** and **time_delta**.")
st.write("From these observations we can deduce that only +/- 8% of cars are rented at least twice, because they have an ID number from the previous rental and a time delta.")
st.write("It can be assumed that approximately `8%` of owners will be affected by the feature")

# Question 1
st.divider()
st.subheader("1. Which share of our owner's revenue would potentially be affected by the feature?")
st.write("To estimate the impact on our owners' revenue, we first need to determine how many rentals per vehicle could be affected by the feature.")
st.write("Since we don't have owner identifiers in the dataset, we'll make a simplifying assumption: each owner has only one vehicle.")
st.write("We'll also assume an average revenue of $120 per rental.")
st.write("The chart below shows the proportion of rentals with less than 720 minutes between two consecutive bookings, depending on the chosen time buffer.")


min_threshold = int(df['time_delta'].min()) if int(df['time_delta'].min()) > 0 else 5
max_threshold = int(df['time_delta'].max())
average_income_per_rental = 120

def get_affected_rentals(threshold):
    affected_rentals = df[df["time_delta"] < threshold]
    return affected_rentals

def get_length_of_affected_rentals(threshold):
    affected_rentals = get_affected_rentals(threshold)
    #print(affected_rentals)
    return len(affected_rentals)

def get_percent_affected(threshold):
    percent = (get_length_of_affected_rentals(threshold) / len(df)) * 100
    return percent

step = 10
time_gaps = range(min_threshold, max_threshold + step, step)
percent_affected = []
for gap in time_gaps:
    percent = get_percent_affected(gap)
    percent_affected.append(percent)

fig = px.bar(
    x=time_gaps,
    y=percent_affected,
    
    labels={
        "x": "Minimum time between two rentals (minutes)",
        "y": "Percentage of rentals affected (%)"
    },
    title="Impact of a minimum time between two rentals"
)
st.plotly_chart(fig)

threshold = st.slider("Choose a threshold (minutes)", min_value=min_threshold, max_value=max_threshold, value=10, step=5)

# Get the percentage of rentals affected
percent_affected_slider = round(get_percent_affected(threshold),2)
total_rentals_affected = get_length_of_affected_rentals(threshold)
#print("TOTAL",total_rentals_affected)

# Calculate the total loss
total_loss = total_rentals_affected * average_income_per_rental
total_loss_dollars = "${:.2F}".format(total_loss)

# Get the number of owners affected
affected_rentals_slider =  get_affected_rentals(threshold)
owner_affected = affected_rentals_slider["car_id"].nunique()
#print(owner_affected)

loss_per_owner = total_loss / owner_affected if owner_affected > 0 else 0
loss_per_owner_dollars = "${:.2F}".format(loss_per_owner)

# display metrics question1
col_1_1, col_1_2, col_1_3, col_1_4 = st.columns(4)
col_1_1.metric("Threshold", threshold, border=True)
col_1_2.metric("% of rental affected", percent_affected_slider, border=True)
col_1_3.metric("Global loss", total_loss_dollars, border=True)
col_1_4.metric("Owner loss    ", loss_per_owner_dollars, border=True)
st.write(":point_right: As we can see, beyond 4% of lost rentals, the economic impact becomes significant for the company (over $100000) ")

# Question 2
st.divider()
st.subheader("2. How many rentals would be affected by the feature depending on the threshold and scope we choose?")
affected_rental_by_checkin_type = affected_rentals_slider["checkin_type"].value_counts()
#print(affected_rental_by_checkin_type)
affected_rental_mobile = affected_rental_by_checkin_type["mobile"]
affected_rental_connect = affected_rental_by_checkin_type["connect"]

# display metrics question2
col_2_1, col_2_2, col_2_3 = st.columns(3)
col_2_1.metric("Total rentals affected", total_rentals_affected, border=True)
col_2_2.metric("Checkin type: Mobile", affected_rental_mobile, border=True)
col_2_3.metric("Checkin type: Connect", affected_rental_connect, border=True)
st.write(":point_right: As you can see, the number of rentals affected by the feature varies from 279 to a maximum of 1711")


# Question 3
st.divider()
st.subheader("3. How often are drivers late for the next check-in?")

# Define the categories and the desired order
categories = ["Early", "On-time +/- 5 min", "Slightly Late <= 60 min", "Very Late"]

# Create the column "delay_category" with a specific order
df["delay_category"] = pd.Categorical(pd.cut(df["delay"], 
                                             bins=[float('-inf'), -5, 5, 60, float('inf')], 
                                             labels=categories),
                                             categories=categories, 
                                             ordered=True)

checkin_counts = df.groupby(["delay_category", "checkin_type"], observed=True).size().reset_index(name="count")

fig = px.bar(checkin_counts, 
             x="delay_category", 
             y="count", 
             color="checkin_type",
             title="Check-in Type Distribution per Delay Category",
             category_orders={"delay_category": categories},
             labels={"checkin_type": "Check-in Type", "delay_category": "Delay Category", "count": "Count"},
             barmode="relative"
            )

st.plotly_chart(fig)

total_early_count = checkin_counts[checkin_counts["delay_category"] == "Early"]["count"].sum()
#print("total_early_count", total_early_count)
total_on_time_count = checkin_counts[checkin_counts["delay_category"] == "On-time +/- 5 min"]["count"].sum()
total_slightly_late_count = checkin_counts[checkin_counts["delay_category"] == "Slightly Late <= 60 min"]["count"].sum()
total_very_late_count = checkin_counts[checkin_counts["delay_category"] == "Very Late"]["count"].sum()
total_late = total_slightly_late_count + total_very_late_count

col_3_1, col_3_2, col_3_3 = st.columns(3)
col_3_1.metric("Total Early", total_early_count, border=True)
col_3_2.metric("Total On time", total_on_time_count, border=True)
col_3_3.metric("Total Late", total_late, border=True)
st.write(":point_right: As we can see, more than half are late. It seems that checkin type connect are less late than mobile.")


st.subheader("How does it impact the next driver?")

df_valid = df.dropna(subset=["delay", "time_delta"]).copy()

# Identifies cases where the previous driver overlaps into the next rental
df_valid["overlap"] = df_valid["delay"] - df_valid["time_delta"]
df_overlap = df_valid[df_valid["overlap"] > 0]

overlap_info = df_overlap.groupby("checkin_type").agg(
    count=("overlap", "count"),
    avg_overlap=("overlap", "mean"),
    max_overlap=("overlap", "max"),
    min_overlap=("overlap", "min"),
    median_overlap=("overlap", "median")
).reset_index()

st.write("Summary of overlapping rentals (when delay exceeds time between rentals in minutes):")
st.dataframe(overlap_info)
st.write(":point_right: As we can see, 270 cases of overlapping.")

fig = px.histogram(
    df_overlap,
    x="overlap",
    color="checkin_type",
    nbins=50,
    title="Distribution of overlap time (in minutes) between two rentals",
    labels={"overlap": "Overlap duration (min)"}
)
st.plotly_chart(fig)
st.write(":point_right: As we can see, most of overlapping time are between 0 and 199 min.")


# Question 4
st.divider()
st.subheader("4. How many problematic cases will it solve depending on the chosen threshold and scope?")

# scope of the feature
scope = st.selectbox("Scope of the feature (check-in type)", options=["all", "connect"])

# threshold in minutes
threshold = st.slider("Minimum time between rentals (minutes)", min_value=0, max_value=720, value=60, step=5)

if scope == "connect":
    df_scope = df_valid[df_valid["checkin_type"] == "connect"]
else:
    df_scope = df_valid.copy()

total_scope = len(df_scope)
#print("total_scope",total_scope)

# conflict cases (where delay > time_delta)
all_conflicts = df_scope[df_scope["delay"] > df_scope["time_delta"]]
total_all_conflicts = len(all_conflicts)
#print("total_all_conflicts : ",total_all_conflicts)

resolved_cases_df = all_conflicts[all_conflicts["time_delta"] < threshold]
resolved_cases = len(resolved_cases_df)
#print("resolved_cases",resolved_cases)

percent_resolved = (resolved_cases / len(all_conflicts)) * 100 if len(all_conflicts) > 0 else 0
problematic_cases = resolved_cases
percent_affected = (problematic_cases / total_scope) * 100 if total_scope > 0 else 0

# Show key metrics
col_4_1, col_4_2, col_4_3, col_4_4, col_4_5 = st.columns(5)
col_4_1.metric("Total problematic cases", total_all_conflicts)
col_4_2.metric("Scope size", total_scope)
col_4_3.metric("Percent affected", f"{percent_affected:.2f}%")
col_4_4.metric("Resolved cases", resolved_cases)
col_4_5.metric("Resolution rate", f"{percent_resolved:.2f}%")

# Show distribution by check-in type
checkin_dist = resolved_cases_df["checkin_type"].value_counts().reset_index()
checkin_dist.columns = ["Check-in Type", "Count"]

fig = px.bar(
    checkin_dist,
    x="Check-in Type",
    y="Count",
    color="Check-in Type",
    title="Distribution of resolved problematic cases by check-in type",
    text="Count"
)
st.plotly_chart(fig)
st.write(":point_right: As we can see, depending on the chosen threshold and scope we can resolve from 136 to 267 of 270 problematic cases.")


# Final question 1
st.divider()
st.subheader("How long should the minimum delay be?")

scope_graph = st.selectbox("Scope (check-in type)", options=["all", "connect"], key="scope_q5")
if scope_graph == "connect":
    df_scope = df_valid[df_valid["checkin_type"] == "connect"]
else:
    df_scope = df_valid.copy()

threshold_range = range(0, 721, 10)  # from 0 to 720 by step of 10
problem_counts = []

for t in threshold_range:
    count = df_scope[
        (df_scope["delay"] > df_scope["time_delta"]) &
        (df_scope["time_delta"] < t)
    ].shape[0]
    problem_counts.append({"Threshold (min)": t, "Problematic Cases": count})

df_plot = pd.DataFrame(problem_counts)

fig = px.line(
    df_plot,
    x="Threshold (min)",
    y="Problematic Cases",
    title="Problematic cases solved vs. Minimum delay threshold",
    markers=True
)
st.plotly_chart(fig)
st.write(":point_right: As can be seen, after a threshold of 130 min the number of resolved cases does not increase significantly. The choice of 130 min seems appropriate.")


# Final question 2
st.divider()
st.subheader("Should we enable the feature for all cars, or only Connect cars?")

decision_threshold = st.slider("Select a decision threshold (minutes)", min_value=0, max_value=720, value=60, step=10)

def count_problematic_cases(data, threshold):
    return data[
        (data["delay"] > data["time_delta"]) &
        (data["time_delta"] < threshold)
    ]

df_all = df_valid.copy()
df_connect = df_valid[df_valid["checkin_type"] == "connect"]
df_mobile = df_valid[df_valid["checkin_type"] == "mobile"]

cases_all = count_problematic_cases(df_all, decision_threshold)
cases_connect = count_problematic_cases(df_connect, decision_threshold)
cases_mobile = count_problematic_cases(df_mobile, decision_threshold)

total_all = len(df_all)
total_connect = len(df_connect)
total_mobile = len(df_mobile)

pct_problematic_case_connect = round(( len(cases_connect) * 100 / len(cases_all)), 2) if len(cases_connect) > 0 else 0
pct_problematic_case_mobile = round(( len(cases_mobile) * 100 / len(cases_all)), 2) if len(cases_mobile) > 0 else 0


col_6_1, col_6_2, col_6_3 = st.columns(3)
col_6_1.metric("Problematic cases : All", len(cases_all), border=True)
col_6_2.metric("Problematic cases : Connect only", f"{len(cases_connect)} ({pct_problematic_case_connect:.1f}%)", border=True)
col_6_3.metric("Problematic cases : Mobile only", f"{len(cases_mobile)} ({pct_problematic_case_mobile:.1f}%)", border=True)

pct_connect = round((len(cases_connect) / total_connect * 100), 2) if total_connect > 0 else 0
pct_mobile = round((len(cases_mobile) / total_mobile * 100), 2) if total_mobile > 0 else 0
pct_total = pct_connect + pct_mobile

col_6_4, col_6_5, col_6_6 = st.columns(3)
col_6_4.metric("Percentage of scope : All",  f"{pct_total:.1f}%", border=True)
col_6_5.metric("Percentage of scope : Connect only", f"{pct_connect:.1f}%", border=True)
col_6_6.metric("Percentage of scope : Mobile only", f"{pct_mobile:.1f}%", border=True)

comparison_df = pd.DataFrame({
    "Check-in Type": ["Connect", "Mobile"],
    "Problematic Cases": [len(cases_connect), len(cases_mobile)],
    "Percentage of Scope": [pct_connect, pct_mobile]
})

fig = px.bar(
    comparison_df,
    x="Check-in Type",
    y="Problematic Cases",
    color="Check-in Type",
    text="Percentage of Scope",
    title=f"Problematic cases by check-in type (threshold = {decision_threshold} min)"
)
st.plotly_chart(fig)
st.write(":point_right: As can be seen, if we choose a threshold of 130 min the number of problematic cases represents more than 30% of all problematic cases, which is significant. The choice to enable the feature for all cars therefore seems relevant.")

