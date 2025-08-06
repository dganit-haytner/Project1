import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt




def categorizing_from_numeric(df):
    # Recode Variable into Categorical
    #st.write("### Categorization (Grouping)")
    #st.write("Optional: creating a categorical variable such as age groups")
    # select a numerical column
    numeric_cols_nu = df.select_dtypes(include='number').columns.tolist()
    selected_col_nu = st.selectbox("Select a column to recode", numeric_cols_nu, key="nu_selected_col")
    st.write("Define the intervals for the new categories:")
    # lower1 = st.number_input("Lower bound for Group 1", value=18)
    # upper1 = st.number_input("Upper bound for Group 1", value=34)
    # Group 1 inputs side by side
    col1, col2 = st.columns(2)
    with col1:
        lower1 = st.number_input("Lower bound", value=18, key="l1")
    with col2:
        upper1 = st.number_input("Upper bound", value=34, key="u1")
    col3, col4 = st.columns(2)
    with col3:
        lower2 = st.number_input("Lower bound", value=35, key="l2")
    with col4:
        upper2 = st.number_input("Upper bound", value=54, key="u2")

    add_group4 = False
    label3 = label4 = ""
    lower3 = upper3 = lower4 = upper4 = None

    add_group3 = st.checkbox("Add a group?")
    if add_group3:
        col5, col6 = st.columns(2)
        with col5:
            lower3 = st.number_input("Lower bound", value=55, key="l3")
        with col6:
            upper3 = st.number_input("Upper bound", value=64, key="u3")
        add_group4 = st.checkbox("add a group?")
        if add_group4:
            col7, col8 = st.columns(2)
            with col7:
                lower4 = st.number_input("Lower bound", value=65, key="l4")
            with col8:
                upper4 = st.number_input("Upper bound", value=90, key="u4")
    label1 = st.text_input("**Label for Group 1**", value="18-34", key="lab1")
    label2 = st.text_input("**Label for Group 2**", value="35-54", key="lab2")
    if add_group3:
        label3 = st.text_input("**Label for Group 3**", value="55-64", key="lab3")
        if add_group4:
            label4 = st.text_input("**Label for Group 4**", value="65-90", key="lab4")
    new_var_name = st.text_input("**Name of the new categorical variable**", value="age_group")

    if st.button("Create Categorical Variable"):
        def recode(val):
            if lower1 <= val <= upper1:
                return label1
            elif lower2 <= val <= upper2:
                return label2
            elif add_group3 and lower3 <= val <= upper3:
                return label3
            elif add_group4 and lower4 <= val <= upper4:
                return label4
            else:
                return 'Other'

        df[new_var_name] = df[selected_col_nu].apply(recode)

        st.session_state.df = df.copy()  # 💡 store updated DataFrame in session_state

        st.success(f"New column '{new_var_name}' created!")
        st.dataframe(df)
        if new_var_name:
            value_counts = df[new_var_name].value_counts().sort_index()
            fig, ax = plt.subplots(figsize=(4, 2))  # 👈 smaller chart
            value_counts.plot(kind='bar', ax=ax)
            ax.set_title(f"{new_var_name}", fontsize=6)
            ax.set_xlabel("")
            ax.tick_params(axis='x', labelsize=6)  # Smaller x-axis labels
            ax.tick_params(axis='y', labelsize=6)  # Smaller y-axis labels
            ax.set_ylabel("Frequency", fontsize=6)
            plt.xticks(rotation=45)
            st.pyplot(fig)
    return df



def categorizing_from_nominal(df):
    # Select only nominal (object or category) columns
    nominal_cols_n = df.select_dtypes(include=['object', 'category']).columns
    selected_col_n = st.selectbox("Select a nominal column to recode", nominal_cols_n, key="nom_selected_col")
    unique_vals_n = df[selected_col_n].unique().tolist()

    group2_vals, group3_vals, group4_vals = [], [], []
    label_n2, label_n3, label_n4 = "", "", ""


    group1_vals = st.multiselect("Select all values for Group 1", options=unique_vals_n, key='grp1')
    label_n1 = st.text_input("Label for Group 1", value="Group A", key='lbl1')
    add_group2 = st.checkbox("Add a second group?", key="add_group2")
    if add_group2:
        group2_vals = st.multiselect("Select all values for Group 2", options=unique_vals_n, key='grp2')
        label_n2 = st.text_input("Label for Group 2", value="Group B", key='lbl2')
    add_group3 = st.checkbox("Add a third group?", key="add_group3")
    if add_group3:
        group3_vals = st.multiselect("Select all values for Group 3", options=unique_vals_n, key='grp3')
        label_n3 = st.text_input("Label for Group 3", value="Group C", key='lbl3')
    add_group4 = st.checkbox("Add a fourth group?", key="add_group4")
    if add_group4:
        group4_vals = st.multiselect("Select all values for Group 4", options=unique_vals_n, key='grp4')
        label_n4 = st.text_input("Label for Group 4", value="Group D", key='lbl4')
    new_cat_var_nom = st.text_input("New variable name", value=f"{selected_col_n}_grouped", key="new_cat_var_nom")

    # Button to create new variable
    if st.button("Create Categorical Variable", key="create_cat_var"):
        def recode_nominal(value):
            if value in group1_vals:
                return label_n1
            elif add_group2 and value in group2_vals:
                return label_n2
            elif add_group3 and value in group3_vals:
                return label_n3
            elif add_group4 and value in group4_vals:
                return label_n4
            else:
                return "Other"

        df[new_cat_var_nom] = df[selected_col_n].apply(recode_nominal) # adding the new var to df

        st.session_state.df = df.copy()  # 💡 store updated DataFrame in session_state


        st.success(f"New column '{new_cat_var_nom}' created!")
        st.dataframe(df)

        value_counts = df[new_cat_var_nom].value_counts().sort_index()
        fig, ax = plt.subplots(figsize=(4, 2)) # 👈 smaller chart
        value_counts.plot(kind='bar', ax=ax)
        ax.set_title(f"{new_cat_var_nom}", fontsize=6)
        ax.set_xlabel("")
        ax.tick_params(axis='x', labelsize=6)  # Smaller x-axis labels
        ax.tick_params(axis='y', labelsize=6)  # Smaller y-axis labels
        ax.set_ylabel("Frequency", fontsize=6)
        plt.xticks(rotation=45)
        st.pyplot(fig)
    return df
