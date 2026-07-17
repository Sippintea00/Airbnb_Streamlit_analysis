import pandas as pd
import altair as alt
import streamlit as st

st.write("**Airbnb Data Analysis**")
st.write(
    "This dashboard helps prospective Airbnb hosts determine which property characteristics are associated with higher occupancy rates and estimated revenue."
)
df = pd.read_csv("listings.csv")



listings = df[['neighbourhood_cleansed','estimated_occupancy_l365d','reviews_per_month', 'price', 'number_of_reviews', 'availability_365','property_type','price_quote_price_per_night','estimated_revenue_l365d','bathrooms','bedrooms','beds','minimum_nights','maximum_nights','review_scores_rating']]


#filter out undesired data
listings = listings.dropna()
listings = listings[listings['number_of_reviews'] > 0]

#condense the property types into 4 categories
property_mapping = {
    # Entire Places
    "Entire loft": "Entire Place",
    "Entire rental unit": "Entire Place",
    "Entire serviced apartment": "Entire Place",
    "Entire condo": "Entire Place",
    "Entire home": "Entire Place",
    "Entire guesthouse": "Entire Place",
    "Entire guest suite": "Entire Place",
    "Entire townhouse": "Entire Place",
    "Entire place": "Entire Place",
    "Tiny home": "Entire Place",
    "Houseboat": "Entire Place",
    "Boat": "Entire Place",

    # Private Rooms
    "Private room in rental unit": "Private Room",
    "Private room in home": "Private Room",
    "Private room in serviced apartment": "Private Room",
    "Private room in townhouse": "Private Room",
    "Private room in condo": "Private Room",
    "Private room in bed and breakfast": "Private Room",
    "Private room in guest suite": "Private Room",

    # Shared Rooms
    "Shared room in rental unit": "Shared Room",
    "Shared room in condo": "Shared Room",

    # Hotel Rooms
    "Room in hotel": "Hotel Room",
    "Room in boutique hotel": "Hotel Room",
    "Room in aparthotel": "Hotel Room",
}

# Create a new column consolidating property type
listings["property_category"] = (
    listings["property_type"]
    .map(property_mapping)
    .fillna("Other")
)

st.sidebar.header("Filters")

# Sidebar Filters
category = st.sidebar.selectbox("Filter By Rental Type", ["All"] + list(listings["property_category"].unique()))

location = st.sidebar.selectbox("Filter By neighborhood", ["All"] + list(listings["neighbourhood_cleansed"].unique()))


revenue_range = st.sidebar.slider("Select Estimated Revenue Range",
     int(listings["estimated_revenue_l365d"].min()), 
     int(listings["estimated_revenue_l365d"].max()), 
         (0, 200000))


#applying dilters
filtered_listings = listings if category == "All" else listings[listings["property_category"] == category]
filtered_listings = filtered_listings if location == "All" else filtered_listings[filtered_listings["neighbourhood_cleansed"] == location]
filtered_listings = filtered_listings[filtered_listings["estimated_revenue_l365d"].between(*revenue_range)]


st.write("*Heatmap of estimated occupancy over the minimum required nights per stay*")

st.altair_chart(
    alt.Chart(filtered_listings).mark_rect().encode(
    x = alt.X('minimum_nights:Q', bin = alt.Bin(maxbins = 20)),
    y = alt.Y('estimated_occupancy_l365d:Q', bin = alt.Bin(maxbins = 20)),
    color = "count():Q",
    tooltip=["mean(estimated_revenue_l365d):Q", "estimated_occupancy_l365d:Q", "minimum_nights:Q","count():Q"]
)
)

st.write("*Estimated price per night over number of bedrooms*")

chart_type = st.radio("Choose Chart Type", ["Scatterplot", "Bar Chart"])

if chart_type == "Scatterplot":
    st.altair_chart(
    alt.Chart(filtered_listings).mark_circle().encode(
    x = alt.X("bedrooms:Q"),
    y = alt.Y("price_quote_price_per_night:Q"),
    #color = "bathrooms:Q",
    tooltip=["price_quote_price_per_night:Q","bedrooms:Q","bathrooms:Q","estimated_revenue_l365d"]
    )
)
else:
    bar_listings = filtered_listings[filtered_listings['price_quote_price_per_night'] < 2000]
    #remove approx 5 outliers for estimated revenue
    
    st.altair_chart(
        alt.Chart(bar_listings).mark_bar().encode(
    x = alt.X("bedrooms:Q"),
    y = alt.Y("price_quote_price_per_night:Q", aggregate = "mean"),
    color = "count():Q",
    tooltip=["mean(price_quote_price_per_night):Q","mean(bedrooms):Q","mean(bathrooms):Q","mean(estimated_revenue_l365d)"]
        )
    )    

st.write("*Estimated annual revenue over the price per night*")

st.altair_chart(
    alt.Chart(filtered_listings).mark_circle().encode(
    x = alt.X('price_quote_price_per_night:Q'),
    y = alt.Y('estimated_revenue_l365d:Q'),
    color = "property_category:N",
    tooltip=["estimated_revenue_l365d", "price_quote_price_per_night:Q", "bedrooms:Q"]
    )
)
    
