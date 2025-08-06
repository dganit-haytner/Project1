import requests
import io
import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from wordcloud import WordCloud
import numpy as np
import helper

st.title("Data Analysis")
st.write("This app is an automatic EDA Generator. It reads your uploaded data file \(CSV or Excel\) or link to such files, "
+ "and provides descriptive statistics and data visualizations \(by scatter plots / column bars and more\). " + "Please see the example below.")

if 'df' not in st.session_state:
    st.session_state.df = None

df = st.session_state.df


# File Upload
uploaded_file = st.file_uploader("**Select a CSV or Excel data file**", type=["csv", "xlsx"])
# or URL Input
url = st.text_input("**OR** paste a **URL** to a CSV or Excel file,\n(e.g. paste this URL:",
                    value="https://raw.githubusercontent.com/mwaskom/seaborn-data/master/iris.csv")

# additional link examples
#https://raw.githubusercontent.com/mwaskom/seaborn-data/master/flights.csv.
#https://raw.githubusercontent.com/mwaskom/seaborn-data/master/geyser.csv.


df = None
# Handle file upload
if uploaded_file is not None:
    if uploaded_file.name.endswith('.csv'):
        df = pd.read_csv(uploaded_file)
    elif uploaded_file.name.endswith('.xlsx'):
        df = pd.read_excel(uploaded_file)
# Handle URL input
elif url:
    try:
        response = requests.get(url)
        response.raise_for_status()
        if url.endswith('.csv'):
            df = pd.read_csv(io.StringIO(response.text))
        elif url.endswith('.xlsx'):
            df = pd.read_excel(io.BytesIO(response.content))
        else:
            st.error("The URL must end with .csv or .xlsx")
    except Exception as e:
        st.error(f"Failed to fetch the file: {e}")

# Display dataframe if loaded
if df is not None:
    st.success("File loaded successfully!")
    # Show dataframe
    st.write("### Data Preview")
    st.write("For sorting or additional options click on the 3 dots on top of each column", df.head(6))
    if 'df' not in st.session_state:
        st.session_state.df = df




cols_with_na = df.columns[df.isnull().any()].tolist()
if not cols_with_na:
    st.write("✅ There are no missing values in the DataFrame.")
else:
    # Filter rows with at least one missing value
    missing_rows = df[df.isnull().any(axis=1)]
    # Sort columns by number of missing values in descending order
    missing_counts = df[cols_with_na].isnull().sum().sort_values(ascending=False)
    sorted_columns = missing_counts.index.tolist()
    # Display the relevant part of the DataFrame
    missing_data_sorted = missing_rows[sorted_columns]
    st.write("⚠️ Rows with missing values:")
    st.write(missing_data_sorted)




if df is not None:
    if 'df' not in st.session_state:
        st.session_state.df = df

    # categorical variables
    st.write("### Categorical Variables")
    # bar chart
    categorical_cols = df.select_dtypes(include=['object', 'category']).columns.tolist()  # selected col
    if categorical_cols:
        for col in categorical_cols:
            # st.subheader(f"Column: {col}")
            value_counts = df[col].value_counts().sort_index()
            #value_counts = df[col].value_counts().sort_values(ascending=False)
            #fig, ax = plt.subplots()
            fig, ax = plt.subplots(figsize=(4, 2))  # 👈 smaller chart
            value_counts.plot(kind='bar', ax=ax)
            ax.set_title(f"{col}", fontsize=6)
            ax.set_xlabel("")
            ax.tick_params(axis='x', labelsize=6)  # Smaller x-axis labels
            ax.tick_params(axis='y', labelsize=6)  # Smaller y-axis labels
            ax.set_ylabel("Frequency", fontsize=6)
            plt.xticks(rotation=45)
            st.pyplot(fig)


    # numeric variables
    st.write("### Numeric Variables")
    descr = df.describe(percentiles=[.25, .5, .75, .01, .99])
    descr.rename(index={'50%': '50% (median)'}, inplace=True)
    descr = descr.round(2)
    #   st.write("For sorting or additional options click on the 3 dots on top of each column", descr)
    st.write("For sorting or additional options click on the 3 dots on top of each column")
    descr = descr.reset_index()
    descr.rename(columns={'index': 'Statistic'}, inplace=True)
    st.dataframe(descr, use_container_width=True)




    # pairplot
    # select vars
    st.write("**Pair Plotting**")
    numeric_cols = df.select_dtypes(include=["number"]).columns.tolist()
    selected_cols = st.multiselect("Select numeric columns", numeric_cols, default=numeric_cols)
    hue_col = st.selectbox("Optional: select a variable for segmentation by color (recommended! 🔥)", ["None"] + df.columns.tolist())
    if selected_cols:
        # Create pairplot
        with st.spinner("Generating pairplot..."):
            try:
                fig = sns.pairplot(df[selected_cols + ([hue_col] if hue_col != "None" else [])],
                                   hue=hue_col if hue_col != "None" else None)
                st.pyplot(fig)
            except Exception as e:
                st.error(f"Error creating pairplot: {e}")
    else:
        st.warning("Please select at least one numeric column.")


    st.write("")
    st.write("")
    st.write("")


    # Creating new categorial variables
    #df = st.session_state.df  # Work with the current stored version

    # creating a new categorical variable out of numeric values
    st.subheader("Optional: Categorizing")
    categorizing_from_numeric_yes = st.checkbox("creating a new **categorical** variable out of **numeric** values"
                                                  + ", e.g. age group out of age", key="categorizing_from_numeric_yes1")
    add_group4 = False
    if categorizing_from_numeric_yes:
        helper.categorizing_from_numeric(df)


    # creating a new categorical variable out of nominal values
    st.subheader("Optional: Additional Categorizing")
    categorizing_from_nominal_yes = st.checkbox("creating a new **categorical** variable out of **nominal** values"
                                                  + ", e.g. quartiles out of month names", key="categorizing_from_nominal_yes1")
    if categorizing_from_nominal_yes:
        helper.categorizing_from_nominal(df)


    st.write("")
    st.write("")
    st.write("")

    df = st.session_state.df
    chart_viewer_yes = st.checkbox("Do you want to use additional charts?", key='chart_viewer_yes')
    if chart_viewer_yes:
        st.subheader("Chart Generator")

        # Select Chart Type
        chart_type = st.selectbox("Select Chart Type", ["Line", "Bar", "Scatter"], key='chart_type')

        # Select columns based on chart type
        if chart_type in ["Line", "Bar"]:
            x_axis = st.selectbox("Select X-axis", df.columns)
            y_axis = st.multiselect("Select Y-axis", df.columns.drop(x_axis))
        elif chart_type == "Scatter":
            x_axis = st.selectbox("Select X-axis", df.columns)
            y_axis = st.selectbox("Select Y-axis", df.columns.drop(x_axis))
            seg = st.selectbox("Select Y-axis", df.columns.drop(x_axis).drop(y_axis))

        if chart_type == "Line":
            if y_axis:
                st.line_chart(df.set_index(x_axis)[y_axis])
            else:
                st.warning("Please select at least one Y-axis column.")

        elif chart_type == "Bar":
            if y_axis:
                st.bar_chart(df.set_index(x_axis)[y_axis])
            else:
                st.warning("Please select at least one Y-axis column.")

        elif chart_type == "Scatter":
            if x_axis and y_axis:
                st.write("Scatter Plot")
                fig, ax = plt.subplots()
                sns.scatterplot(x=x_axis, y=y_axis, data=df, hue=seg, size=seg, ax=ax)
                st.pyplot(fig)
            else:
                st.warning("Please select both X and Y axes.")




    st.write("")
    st.write("")
    st.write("")

    df = st.session_state.df
    # violin plot.
    st.write("### Violin Plot")
    available_palettes = ["deep", "muted", "pastel", "bright", "dark", "colorblind"]
    x_var = st.selectbox("Select X (categorical):", df.select_dtypes(include='object').columns)
    y_var = st.selectbox("Select Y (numeric):", df.select_dtypes(include='number').columns)
    hue_var = st.selectbox("Select segmentation (categorical):", df.select_dtypes(include='object').columns)
    palette_choice = st.selectbox("Choose a color palette:", available_palettes)
    if st.button("Generate Plot"):
        fig, ax = plt.subplots()
        sns.violinplot(data=df, x=x_var, y=y_var, hue=hue_var,
                       split=True, inner="quart", fill=False,
                       palette=palette_choice, ax=ax)
        st.pyplot(fig)

    st.write("")
    st.write("")
    st.write("")


    df = st.session_state.df
    # wordcloud.
    st.subheader("Word Cloud Generator ☁️")
    wordcloud_column_yes = st.checkbox("Add WordCloud? \n(recommended for TEXT columns)", key='wordcloud_column_yes')

    # Identify text (object or string) columns only
    text_columns = df.select_dtypes(include=['object', 'string']).columns.tolist()

    if wordcloud_column_yes:
        wordcloud_column = st.selectbox("Select the TEXT column to generate a Word Cloud from", text_columns, key='wordcloud_column')

        def preprocess_text(series):
            # Split comma-separated entries, flatten list, strip whitespace
            # words = []
            words = set()
            for entry in series.dropna().astype(str):
                for word in entry.split(','):
                    words.add(word.strip().lower())  # lowercasing helps avoid duplicates like "Python" vs "python"
            return ' '.join(words)
        text = preprocess_text(df[wordcloud_column])

        # Generate WordCloud
        if text:
            wc = WordCloud(width=800, height=400, background_color='white').generate(text)
            # Show the plot
            fig, ax = plt.subplots(figsize=(10, 5))
            ax.imshow(wc, interpolation='bilinear')
            ax.axis('off')
            st.pyplot(fig)
        else:
            st.warning("Selected column is empty or invalid.")


#st.session_state.df = df


# st.link_button("Profile", url="/profile")

#run in terminal after finish coding
# poetry export -f requirements.txt --with dev --output requirements.txt --without-hashes

# streamlit run main.py