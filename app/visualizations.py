"""
Visualization components for the Streamlit app.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go


def display_statistics(df: pd.DataFrame):
    """
    Display basic statistics about the chat with modern styling.
    
    Args:
        df: DataFrame with message data
    """
    st.markdown('<h2 class="section-header">📊 Overview</h2>', unsafe_allow_html=True)
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="💬 Total Messages", 
            value=f"{len(df):,}",
            delta="All time"
        )
    
    with col2:
        st.metric(
            label="👥 Participants", 
            value=df['sender'].nunique(),
            delta=f"{df['sender'].nunique()} unique"
        )
    
    with col3:
        if 'datetime' in df.columns and len(df) > 0:
            days = (df['datetime'].max() - df['datetime'].min()).days
            st.metric(
                label="📅 Duration", 
                value=f"{days} days",
                delta=f"{df['datetime'].min().strftime('%b %Y')} - {df['datetime'].max().strftime('%b %Y')}"
            )
        else:
            st.metric("📅 Duration", "N/A")
    
    with col4:
        avg_msg_length = df['text'].str.len().mean()
        st.metric(
            label="📝 Avg Length", 
            value=f"{avg_msg_length:.0f}",
            delta="characters per message"
        )


def display_sender_stats(df: pd.DataFrame):
    """
    Display statistics by sender with modern visualizations.
    
    Args:
        df: DataFrame with message data
    """
    st.markdown('<h2 class="section-header">👥 Participant Analysis</h2>', unsafe_allow_html=True)
    
    # Calculate messages per sender
    sender_stats = df['sender'].value_counts().reset_index()
    sender_stats.columns = ['Sender', 'Messages']
    sender_stats['Percentage'] = (sender_stats['Messages'] / len(df) * 100).round(1)
    
    col1, col2 = st.columns([2, 3])
    
    with col1:
        # Create a styled dataframe
        st.markdown("### Top Contributors")
        # Display without background gradient to avoid matplotlib dependency
        display_df = sender_stats.head(10).copy()
        display_df['Percentage'] = display_df['Percentage'].apply(lambda x: f"{x:.1f}%")
        st.dataframe(display_df, use_container_width=True, hide_index=True)
    
    with col2:
        # Create an interactive donut chart
        fig = go.Figure(data=[go.Pie(
            labels=sender_stats['Sender'].head(10), 
            values=sender_stats['Messages'].head(10),
            hole=.4,
            marker=dict(
                colors=px.colors.sequential.Viridis,
                line=dict(color='white', width=2)
            ),
            textposition='inside',
            textinfo='percent+label',
            hovertemplate='<b>%{label}</b><br>' +
                          'Messages: %{value}<br>' +
                          'Percentage: %{percent}<br>' +
                          '<extra></extra>'
        )])
        
        fig.update_layout(
            title={
                'text': 'Message Distribution by Participant',
                'x': 0.5,
                'xanchor': 'center',
                'font': {'size': 20}
            },
            showlegend=False,
            height=400,
            margin=dict(t=60, b=0, l=0, r=0)
        )
        
        st.plotly_chart(fig, use_container_width=True)


def display_time_analysis(df: pd.DataFrame):
    """
    Display time-based analysis with modern charts.
    
    Args:
        df: DataFrame with message data
    """
    if 'datetime' not in df.columns or len(df) == 0:
        st.warning("⚠️ No datetime information available for time analysis")
        return
    
    st.markdown('<h2 class="section-header">📅 Temporal Patterns</h2>', unsafe_allow_html=True)
    
    # Add time grouping columns
    df['date'] = df['datetime'].dt.date
    df['week'] = df['datetime'].dt.to_period('W').dt.start_time
    df['month'] = df['datetime'].dt.to_period('M').dt.start_time
    df['year'] = df['datetime'].dt.year
    df['hour'] = df['datetime'].dt.hour
    df['weekday'] = df['datetime'].dt.day_name()
    
    # Timeline controls
    st.markdown("### 📈 Message Timeline")
    col1, col2, col3 = st.columns([2, 2, 8])
    
    with col1:
        time_grouping = st.selectbox(
            "Time Grouping",
            ["Daily", "Weekly", "Monthly", "Yearly"],
            index=0
        )
    
    with col2:
        breakdown_by = st.selectbox(
            "View By",
            ["Total", "By Participant"],
            index=0
        )
    
    # Prepare data based on grouping
    if time_grouping == "Daily":
        group_col = 'date'
        date_format = '%Y-%m-%d'
    elif time_grouping == "Weekly":
        group_col = 'week'
        date_format = '%Y-%m-%d'
    elif time_grouping == "Monthly":
        group_col = 'month'
        date_format = '%Y-%m'
    else:  # Yearly
        group_col = 'year'
        date_format = '%Y'
    
    # Create timeline figure
    fig_timeline = go.Figure()
    
    if breakdown_by == "Total":
        # Group by time period
        grouped_messages = df.groupby(group_col).size().reset_index(name='count')
        
        # Add bar chart
        fig_timeline.add_trace(go.Bar(
            x=grouped_messages[group_col],
            y=grouped_messages['count'],
            name=f'{time_grouping} Messages',
            marker_color='lightblue',
            opacity=0.7,
            hovertemplate=f'<b>%{{x|{date_format}}}</b><br>Messages: %{{y}}<extra></extra>'
        ))
        
        # Add moving average for daily/weekly views
        if time_grouping in ["Daily", "Weekly"]:
            window = 7 if time_grouping == "Daily" else 4
            grouped_messages['moving_avg'] = grouped_messages['count'].rolling(window=window, min_periods=1).mean()
            
            fig_timeline.add_trace(go.Scatter(
                x=grouped_messages[group_col],
                y=grouped_messages['moving_avg'],
                name=f'{window}-period Average',
                line=dict(color='darkblue', width=3),
                mode='lines',
                hovertemplate=f'<b>%{{x|{date_format}}}</b><br>Average: %{{y:.1f}}<extra></extra>'
            ))
    
    else:  # By Participant
        # Get top participants
        top_senders = df['sender'].value_counts().head(5).index.tolist()
        colors = px.colors.qualitative.Set3[:len(top_senders)]
        
        for i, sender in enumerate(top_senders):
            sender_df = df[df['sender'] == sender]
            grouped = sender_df.groupby(group_col).size().reset_index(name='count')
            
            fig_timeline.add_trace(go.Scatter(
                x=grouped[group_col],
                y=grouped['count'],
                name=sender,
                mode='lines+markers',
                line=dict(width=2, color=colors[i]),
                marker=dict(size=6),
                hovertemplate=f'<b>{sender}</b><br>%{{x|{date_format}}}<br>Messages: %{{y}}<extra></extra>'
            ))
    
    fig_timeline.update_layout(
        title={
            'text': f'Messages {time_grouping} - {breakdown_by}',
            'x': 0.5,
            'xanchor': 'center',
            'font': {'size': 20}
        },
        xaxis_title='Time Period',
        yaxis_title='Number of Messages',
        hovermode='x unified',
        showlegend=True,
        height=450,
        template='plotly_white'
    )
    
    st.plotly_chart(fig_timeline, use_container_width=True)
    
    # Heatmap and radial chart with normalization
    st.markdown("### 🔥 Activity Patterns")
    
    # Normalization control
    norm_col1, norm_col2 = st.columns([2, 10])
    with norm_col1:
        normalization = st.selectbox(
            "Normalize By",
            ["None", "By Day", "By Hour"],
            index=0
        )
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Create heatmap data
        heatmap_data = df.groupby(['weekday', 'hour']).size().reset_index(name='count')
        heatmap_pivot = heatmap_data.pivot(index='weekday', columns='hour', values='count').fillna(0)
        
        # Reorder weekdays
        weekday_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        heatmap_pivot = heatmap_pivot.reindex(weekday_order)
        
        # Apply normalization
        if normalization == "By Day":
            # Normalize each row (day) to percentages
            heatmap_pivot = heatmap_pivot.div(heatmap_pivot.sum(axis=1), axis=0) * 100
            hover_template = '%{y}<br>%{x}:00<br>%{z:.1f}% of day<extra></extra>'
            colorbar_title = "% of Day"
        elif normalization == "By Hour":
            # Normalize each column (hour) to percentages
            heatmap_pivot = heatmap_pivot.div(heatmap_pivot.sum(axis=0), axis=1) * 100
            hover_template = '%{y}<br>%{x}:00<br>%{z:.1f}% of hour<extra></extra>'
            colorbar_title = "% of Hour"
        else:
            hover_template = '%{y}<br>%{x}:00<br>Messages: %{z}<extra></extra>'
            colorbar_title = "Messages"
        
        fig_heatmap = go.Figure(data=go.Heatmap(
            z=heatmap_pivot.values,
            x=heatmap_pivot.columns,
            y=heatmap_pivot.index,
            colorscale='Viridis',
            hovertemplate=hover_template,
            colorbar=dict(title=colorbar_title)
        ))
        
        fig_heatmap.update_layout(
            title={
                'text': f'Activity Heatmap{" (Normalized)" if normalization != "None" else ""}',
                'x': 0.5,
                'xanchor': 'center'
            },
            xaxis_title='Hour of Day',
            yaxis_title='Day of Week',
            height=400
        )
        
        st.plotly_chart(fig_heatmap, use_container_width=True)
    
    with col2:
        # Radial chart for hours
        hourly_dist = df['hour'].value_counts().sort_index()
        
        # Apply normalization for radial chart
        if normalization != "None":
            hourly_dist = (hourly_dist / hourly_dist.sum()) * 100
            hover_template = 'Hour: %{theta}<br>%{r:.1f}%<extra></extra>'
            radial_range = [0, hourly_dist.max() * 1.1]
        else:
            hover_template = 'Hour: %{theta}<br>Messages: %{r}<extra></extra>'
            radial_range = [0, hourly_dist.max() * 1.1]
        
        fig_radial = go.Figure()
        
        fig_radial.add_trace(go.Barpolar(
            r=hourly_dist.values,
            theta=hourly_dist.index * 15,  # Convert to degrees
            width=15,
            marker_color=hourly_dist.values,
            marker_colorscale='Viridis',
            hovertemplate=hover_template
        ))
        
        fig_radial.update_layout(
            title={
                'text': f'24-Hour Pattern{" (Normalized)" if normalization != "None" else ""}',
                'x': 0.5,
                'xanchor': 'center'
            },
            polar=dict(
                radialaxis=dict(
                    visible=True,
                    range=radial_range,
                    ticksuffix='%' if normalization != "None" else ''
                ),
                angularaxis=dict(
                    tickmode='array',
                    tickvals=list(range(0, 360, 15)),
                    ticktext=[str(i) for i in range(24)]
                )
            ),
            showlegend=False,
            height=400
        )
        
        st.plotly_chart(fig_radial, use_container_width=True)


def display_word_stats(df: pd.DataFrame):
    """
    Display word frequency analysis.
    
    Args:
        df: DataFrame with message data
    """
    st.markdown('<h2 class="section-header">📝 Content Analysis</h2>', unsafe_allow_html=True)
    
    # Get all words
    all_text = ' '.join(df['text'].dropna().astype(str))
    words = all_text.lower().split()
    
    # Filter common words
    common_words = ['the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 
                    'of', 'with', 'by', 'from', 'is', 'was', 'are', 'were', 'been', 'be',
                    'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could',
                    'should', 'may', 'might', 'must', 'can', 'this', 'that', 'these',
                    'those', 'i', 'you', 'he', 'she', 'it', 'we', 'they', 'them', 'their']
    
    filtered_words = [word for word in words if len(word) > 3 and word not in common_words]
    
    # Count word frequency
    word_freq = pd.Series(filtered_words).value_counts().head(20)
    
    # Create bar chart
    fig = go.Figure(data=[
        go.Bar(
            x=word_freq.values,
            y=word_freq.index,
            orientation='h',
            marker=dict(
                color=word_freq.values,
                colorscale='Viridis',
                showscale=False
            ),
            hovertemplate='<b>%{y}</b><br>Count: %{x}<extra></extra>'
        )
    ])
    
    fig.update_layout(
        title={
            'text': 'Top 20 Most Frequent Words',
            'x': 0.5,
            'xanchor': 'center',
            'font': {'size': 20}
        },
        xaxis_title='Frequency',
        yaxis_title='Words',
        height=500,
        yaxis={'categoryorder': 'total ascending'},
        template='plotly_white'
    )
    
    st.plotly_chart(fig, use_container_width=True)