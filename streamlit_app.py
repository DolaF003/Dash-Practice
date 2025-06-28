import streamlit as st
import pandas as pd
import numpy as np
import altair as alt

# Set page config
st.set_page_config(
    page_title="Antibiotic Effectiveness Analysis",
    page_icon="🧬",
    layout="wide"
)

# Title and intro
st.title("🧬 Penicillin's Achilles' Heel: The Gram Staining Divide")
st.markdown("### *Why bacterial cell wall structure determines antibiotic effectiveness*")

# Load data from JSON file
@st.cache_data
def load_and_transform_data():
    import json
    
    # Load the JSON data
    with open('Penicillin Data.json', 'r') as f:
        raw_data = json.load(f)
    
    # Transform to long format
    transformed_data = []
    for record in raw_data:
        for antibiotic in ['Penicillin', 'Streptomycin', 'Neomycin']:
            transformed_data.append({
                'bacteria': record['Bacteria'],
                'antibiotic': antibiotic,
                'mic': record[antibiotic],
                'gram_staining': record['Gram_Staining'],
                'genus': record['Genus'],
                'log_mic': np.log10(record[antibiotic])
            })
    
    return pd.DataFrame(transformed_data)

df = load_and_transform_data()

# Calculate key statistics
gram_pos_pen = df[(df['gram_staining'] == 'positive') & (df['antibiotic'] == 'Penicillin')]['mic'].mean()
gram_neg_pen = df[(df['gram_staining'] == 'negative') & (df['antibiotic'] == 'Penicillin')]['mic'].mean()
effectiveness_ratio = gram_neg_pen / gram_pos_pen

# Key findings section
st.markdown("---")
st.markdown("## 🔬 The Main Discovery")

col1, col2, col3 = st.columns(3)

with col1:
    st.metric(
        label="Effectiveness Ratio",
        value=f"{effectiveness_ratio:.0f}:1",
        help="How many times less effective Penicillin is against Gram-negative vs Gram-positive bacteria"
    )

with col2:
    st.metric(
        label="Gram-positive Avg MIC",
        value=f"{gram_pos_pen:.3f} μg/ml",
        help="Lower MIC = more effective antibiotic"
    )

with col3:
    st.metric(
        label="Gram-negative Avg MIC", 
        value=f"{gram_neg_pen:.1f} μg/ml",
        help="Lower MIC = more effective antibiotic"
    )

st.markdown(f"""
### 💡 **Key Insight: Penicillin is {effectiveness_ratio:.0f}x more effective against Gram-positive bacteria!**

This dramatic difference explains why some infections respond beautifully to penicillin (like strep throat from *Streptococcus*) 
while others seem completely immune (like UTIs from *E. coli*).
""")

# Main visualization
st.markdown("---")
st.markdown("## 📊 The Data Story")

# Create the scatter plot using Altair
scatter_plot = alt.Chart(df).mark_circle(
    size=150,
    stroke='white',
    strokeWidth=2,
    opacity=0.8
).encode(
    x=alt.X('antibiotic:O', 
            title='Antibiotic Type',
            axis=alt.Axis(labelFontSize=12, titleFontSize=14)),
    y=alt.Y('mic:Q', 
            scale=alt.Scale(type='log', base=10),
            title='Minimum Inhibitory Concentration (μg/ml)',
            axis=alt.Axis(labelFontSize=12, titleFontSize=14)),
    color=alt.Color('gram_staining:N',
                   title='Gram Staining',
                   scale=alt.Scale(domain=['positive', 'negative'], 
                                 range=['#3498db', '#e74c3c']),
                   legend=alt.Legend(titleFontSize=14, labelFontSize=12, 
                                   symbolSize=200, orient='top-right')),
    tooltip=['bacteria:N', 'antibiotic:N', 'mic:Q', 'gram_staining:N']
).properties(
    width=700,
    height=400,
    title=alt.TitleParams(
        text=['Antibiotic Effectiveness by Bacterial Type',
              'Lower MIC values indicate higher effectiveness (logarithmic scale)'],
        fontSize=16,
        anchor='start'
    )
)

# Add text annotations
penicillin_text = alt.Chart(pd.DataFrame([{
    'x': 0, 'y': 200,
    'text': f'Penicillin is {effectiveness_ratio:.0f}x less effective\nagainst Gram-negative bacteria!'
}])).mark_text(
    align='center',
    baseline='middle',
    fontSize=12,
    fontWeight='bold',
    color='#c0392b'
).encode(
    x=alt.value(150),
    y=alt.value(80),
    text='text:N'
)

contrast_text = alt.Chart(pd.DataFrame([{
    'text': 'Streptomycin & Neomycin:\nOpposite pattern!'
}])).mark_text(
    align='center',
    baseline='middle',
    fontSize=12,
    fontWeight='bold',
    color='#27ae60'
).encode(
    x=alt.value(550),
    y=alt.value(350),
    text='text:N'
)

# Combine the plot with annotations
main_chart = scatter_plot + penicillin_text + contrast_text

st.altair_chart(main_chart, use_container_width=True)

# Side-by-side comparison for Penicillin
col1, col2 = st.columns(2)

with col1:
    # Bar chart comparing Penicillin effectiveness using Altair
    comparison_data = pd.DataFrame([
        {'Gram_Type': 'Gram-positive', 'Avg_MIC': gram_pos_pen},
        {'Gram_Type': 'Gram-negative', 'Avg_MIC': gram_neg_pen}
    ])
    
    bar_chart = alt.Chart(comparison_data).mark_bar(
        opacity=0.8,
        stroke='white',
        strokeWidth=2
    ).encode(
        x=alt.X('Gram_Type:O', 
                title='Bacterial Type',
                axis=alt.Axis(labelFontSize=12, titleFontSize=14)),
        y=alt.Y('Avg_MIC:Q', 
                scale=alt.Scale(type='log'),
                title='Average MIC (μg/ml)',
                axis=alt.Axis(labelFontSize=12, titleFontSize=14)),
        color=alt.Color('Gram_Type:N',
                       scale=alt.Scale(domain=['Gram-positive', 'Gram-negative'], 
                                     range=['#3498db', '#e74c3c']),
                       legend=None),
        tooltip=['Gram_Type:N', 'Avg_MIC:Q']
    ).properties(
        width=300,
        height=400,
        title=alt.TitleParams(
            text='Penicillin: The Dramatic Effectiveness Gap',
            fontSize=14
        )
    )
    
    # Add value labels on bars
    bar_labels = alt.Chart(comparison_data).mark_text(
        align='center',
        baseline='bottom',
        dy=-5,
        fontSize=11,
        fontWeight='bold'
    ).encode(
        x='Gram_Type:O',
        y=alt.Y('Avg_MIC:Q', scale=alt.Scale(type='log')),
        text=alt.Text('Avg_MIC:Q', format='.3f')
    )
    
    final_bar_chart = bar_chart + bar_labels
    st.altair_chart(final_bar_chart, use_container_width=True)

with col2:
    # Summary statistics table
    st.markdown("### 📈 Effectiveness Summary")
    
    summary_stats = []
    for antibiotic in ['Penicillin', 'Streptomycin', 'Neomycin']:
        antibiotic_data = df[df['antibiotic'] == antibiotic]
        pos_avg = antibiotic_data[antibiotic_data['gram_staining'] == 'positive']['mic'].mean()
        neg_avg = antibiotic_data[antibiotic_data['gram_staining'] == 'negative']['mic'].mean()
        ratio = neg_avg / pos_avg
        
        summary_stats.append({
            'Antibiotic': antibiotic,
            'Gram+ Avg (μg/ml)': f"{pos_avg:.3f}",
            'Gram- Avg (μg/ml)': f"{neg_avg:.3f}",
            'Ratio (Neg/Pos)': f"{ratio:.1f}x"
        })
    
    summary_df = pd.DataFrame(summary_stats)
    st.dataframe(summary_df, use_container_width=True)

# Scientific explanation
st.markdown("---")
st.markdown("## 🧬 The Science Behind the Story")

col1, col2 = st.columns(2)

with col1:
    st.markdown("""
    ### Why Does This Happen?
    
    **Penicillin's Mechanism:**
    - Targets peptidoglycan synthesis in bacterial cell walls
    - Gram-positive bacteria have thick, exposed peptidoglycan layers
    - Gram-negative bacteria have an outer membrane "shield"
    
    **The Outer Membrane Barrier:**
    - Acts like a protective fortress wall
    - Prevents many antibiotics from reaching their targets
    - Makes Gram-negative bacteria inherently more resistant
    """)

with col2:
    st.markdown("""
    ### Clinical Implications
    
    **Why This Matters for Treatment:**
    - Rapid bacterial identification is crucial
    - Gram staining is often the first diagnostic test
    - Different antibiotics needed for different bacterial types
    
    **Real-World Examples:**
    - Strep throat (Gram+): Penicillin works great
    - E. coli UTI (Gram-): Need different antibiotics
    - MRSA infections: Require specialized treatment
    """)

# Detailed analysis section
st.markdown("---")
st.markdown("## 🎯 Most vs Least Effective Cases")

col1, col2 = st.columns(2)

with col1:
    st.markdown("### 🏆 Most Effective (Lowest MIC)")
    most_effective = []
    for antibiotic in ['Penicillin', 'Streptomycin', 'Neomycin']:
        best = df[df['antibiotic'] == antibiotic].loc[df[df['antibiotic'] == antibiotic]['mic'].idxmin()]
        most_effective.append({
            'Antibiotic': antibiotic,
            'Bacteria': best['bacteria'],
            'MIC (μg/ml)': best['mic'],
            'Gram Staining': best['gram_staining']
        })
    
    most_df = pd.DataFrame(most_effective)
    st.dataframe(most_df, use_container_width=True)

with col2:
    st.markdown("### ❌ Least Effective (Highest MIC)")
    least_effective = []
    for antibiotic in ['Penicillin', 'Streptomycin', 'Neomycin']:
        worst = df[df['antibiotic'] == antibiotic].loc[df[df['antibiotic'] == antibiotic]['mic'].idxmax()]
        least_effective.append({
            'Antibiotic': antibiotic,
            'Bacteria': worst['bacteria'],
            'MIC (μg/ml)': worst['mic'],
            'Gram Staining': worst['gram_staining']
        })
    
    least_df = pd.DataFrame(least_effective)
    st.dataframe(least_df, use_container_width=True)

# Interactive data explorer
st.markdown("---")
st.markdown("## 🔍 Explore the Data")

st.markdown("### Filter by bacterial characteristics:")
col1, col2 = st.columns(2)

with col1:
    selected_gram = st.selectbox("Select Gram Staining:", ['All', 'positive', 'negative'])
    
with col2:
    selected_antibiotic = st.selectbox("Select Antibiotic:", ['All', 'Penicillin', 'Streptomycin', 'Neomycin'])

# Filter data based on selections
filtered_df = df.copy()
if selected_gram != 'All':
    filtered_df = filtered_df[filtered_df['gram_staining'] == selected_gram]
if selected_antibiotic != 'All':
    filtered_df = filtered_df[filtered_df['antibiotic'] == selected_antibiotic]

st.dataframe(filtered_df, use_container_width=True)

# Methodology section
st.markdown("---")
st.markdown("## 📚 About This Analysis")

with st.expander("Understanding the Data"):
    st.markdown("""
    **Minimum Inhibitory Concentration (MIC):**
    - The lowest concentration of antibiotic needed to prevent bacterial growth
    - Lower values indicate more effective antibiotics
    - Measured in micrograms per milliliter (μg/ml)
    
    **Gram Staining:**
    - A fundamental bacterial classification method
    - Based on cell wall structure differences
    - Gram-positive: thick peptidoglycan wall, purple staining
    - Gram-negative: thin peptidoglycan + outer membrane, pink staining
    
    **Why We Use Log Scale:**
    - MIC values range from 0.001 to 870 μg/ml (870,000x difference!)
    - Log scale makes patterns visible across this huge range
    - Each step represents a 10-fold change in effectiveness
    """)

st.markdown("---")
st.markdown("*This analysis demonstrates how fundamental biological differences drive clinical decision-making in antibiotic therapy.*")
