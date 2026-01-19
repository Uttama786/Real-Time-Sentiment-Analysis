"""
Interactive Dashboard for Real-time Sentiment Visualization
"""
import os
import sys
import requests
from datetime import datetime, timedelta
import dash
from dash import dcc, html
from dash.dependencies import Input, Output, State
import plotly.graph_objs as go
import plotly.express as px
import dash_bootstrap_components as dbc

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models.processing_comparison import ProcessingComparison

# API endpoint
API_URL = os.getenv('API_URL', 'http://localhost:8000')

# Initialize comparison framework
comparison_framework = ProcessingComparison()

# Initialize Dash app
app = dash.Dash(
    __name__,
    external_stylesheets=[dbc.themes.BOOTSTRAP],
    title="Sentiment Analysis Dashboard"
)

# Layout
app.layout = dbc.Container([
    dbc.Row([
        dbc.Col([
            html.H1("Real-Time Sentiment Analysis Dashboard", 
                   className="text-center mb-4 mt-4"),
            html.Div([
                html.P(id="last-sync-time", className="text-center text-muted small"),
                html.P(id="last-refresh-time", className="text-center text-muted small")
            ]),
            html.Hr()
        ])
    ]),
    
    # Stats Cards
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H4("Total Records", className="card-title"),
                    html.H2(id="total-records", className="text-primary")
                ])
            ])
        ], width=3),
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H4("Average Score", className="card-title"),
                    html.H2(id="avg-score", className="text-info")
                ])
            ])
        ], width=3),
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H4("Positive", className="card-title"),
                    html.H2(id="positive-count", className="text-success")
                ])
            ])
        ], width=3),
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H4("Negative", className="card-title"),
                    html.H2(id="negative-count", className="text-danger")
                ])
            ])
        ], width=3),
    ], className="mb-4"),
    
    # Time range selector
    dbc.Row([
        dbc.Col([
            html.Label("Time Range:"),
            dcc.Dropdown(
                id='timerange-dropdown',
                options=[
                    {'label': 'Last Hour', 'value': '1h'},
                    {'label': 'Last 6 Hours', 'value': '6h'},
                    {'label': 'Last 24 Hours', 'value': '24h'},
                    {'label': 'Last 7 Days', 'value': '7d'},
                    {'label': 'Last 30 Days', 'value': '30d'},
                ],
                value='24h',
                clearable=False
            )
        ], width=3)
    ], className="mb-4"),
    
    # Charts
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H4("Sentiment Distribution", className="card-title"),
                    dcc.Graph(id='sentiment-pie-chart')
                ])
            ])
        ], width=6),
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H4("Source Distribution", className="card-title"),
                    dcc.Graph(id='source-bar-chart')
                ])
            ])
        ], width=6),
    ], className="mb-4"),
    
    # Time series chart
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H4("Sentiment Trends Over Time", className="card-title"),
                    dcc.Graph(id='sentiment-timeline')
                ])
            ])
        ])
    ], className="mb-4"),
    
    # Recent sentiments table
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H4("Recent Sentiments", className="card-title"),
                    html.Div(id='recent-sentiments-table')
                ])
            ])
        ])
    ], className="mb-4"),
    
    # Comments & Insights Section
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H4("📊 Insights & Analysis Comments", className="card-title text-info"),
                    html.Div(id='insights-comments', className="alert alert-light")
                ])
            ])
        ], width=6),
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H4("🎯 Key Metrics", className="card-title text-success"),
                    html.Div(id='key-metrics', className="alert alert-light")
                ])
            ])
        ], width=6)
    ], className="mb-4"),
    
    # Expected vs Predicted Table
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H4("Expected vs Predicted Analysis", className="card-title text-warning"),
                    html.Div([
                        html.P("Shows sentiment classification accuracy and confidence metrics:", 
                               className="text-muted small"),
                        html.Div(id='expected-predicted-table')
                    ])
                ])
            ])
        ])
    ], className="mb-4"),
    
    # Processing Comparison Section
    html.Hr(),
    dbc.Row([
        dbc.Col([
            html.H2("Batch vs Stream Processing Comparison", className="text-center mb-3"),
        ])
    ]),
    
    # Comparison controls
    dbc.Row([
        dbc.Col([
            dbc.Button("Run Comparison Test", id="run-comparison-btn", color="primary", size="lg", className="mb-3"),
            html.Div(id="comparison-status", className="mb-3")
        ], width=12)
    ]),
    
    # Processing Flow Charts
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H4("Batch Processing Flow", className="card-title text-center"),
                    dcc.Graph(id='batch-flow-chart')
                ])
            ])
        ], width=6),
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H4("Stream Processing Flow", className="card-title text-center"),
                    dcc.Graph(id='stream-flow-chart')
                ])
            ])
        ], width=6),
    ], className="mb-4"),
    
    # Performance Comparison Charts
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H4("Throughput Comparison", className="card-title"),
                    dcc.Graph(id='throughput-comparison-chart')
                ])
            ])
        ], width=4),
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H4("Latency Comparison", className="card-title"),
                    dcc.Graph(id='latency-comparison-chart')
                ])
            ])
        ], width=4),
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H4("Total Time Comparison", className="card-title"),
                    dcc.Graph(id='time-comparison-chart')
                ])
            ])
        ], width=4),
    ], className="mb-4"),
    
    # Comparison Table
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H4("Detailed Comparison", className="card-title"),
                    html.Div(id='comparison-table')
                ])
            ])
        ])
    ], className="mb-4"),
    
    # Auto-refresh - more frequent for real-time updates
    dcc.Interval(
        id='interval-component',
        interval=5*1000,  # Update every 5 seconds for real-time feel
        n_intervals=0
    ),
    
    # Store for comparison data
    dcc.Store(id='comparison-data-store')
    
], fluid=True)


# Callbacks

def generate_insights(total_records, avg_score, positive_count, negative_count, neutral_count, sentiment_dist, source_dist):
    """Generate AI-like insights and comments about the data"""
    
    if total_records == 0:
        return html.Div([
            html.P("📋 No data available yet. Start ingestion service to see insights.", 
                   className="text-muted")
        ])
    
    # Calculate percentages
    pos_pct = (positive_count / total_records * 100) if total_records > 0 else 0
    neg_pct = (negative_count / total_records * 100) if total_records > 0 else 0
    neu_pct = (neutral_count / total_records * 100) if total_records > 0 else 0
    
    # Generate insights based on data
    insights = []
    
    # Sentiment trend insight
    if pos_pct > 60:
        insights.append("✅ Overall sentiment is POSITIVE. Strong customer satisfaction detected.")
    elif neg_pct > 60:
        insights.append("⚠️ Overall sentiment is NEGATIVE. Potential issues need attention.")
    else:
        insights.append("🔄 Mixed sentiment distribution indicates diverse feedback.")
    
    # Avg score insight
    if avg_score > 0.5:
        insights.append(f"📈 Average score of {avg_score:.3f} suggests good overall sentiment.")
    elif avg_score < -0.5:
        insights.append(f"📉 Average score of {avg_score:.3f} indicates below-average sentiment.")
    else:
        insights.append(f"🟡 Average score of {avg_score:.3f} reflects neutral sentiment.")
    
    # Data volume insight
    if total_records > 1000:
        insights.append(f"🎯 Large dataset ({total_records} records) provides reliable insights.")
    elif total_records > 100:
        insights.append(f"✓ Moderate dataset ({total_records} records) gives reasonable insights.")
    else:
        insights.append(f"ℹ️ Limited data ({total_records} records). More samples recommended.")
    
    # Source diversity
    if len(source_dist) > 1:
        insights.append(f"🔀 Data from {len(source_dist)} sources provides diverse perspective.")
    else:
        insights.append("🔹 Single data source. Consider adding more sources for broader coverage.")
    
    return html.Div([
        html.Ul([html.Li(insight) for insight in insights], 
                className="list-unstyled text-dark")
    ])


def generate_key_metrics(total_records, positive_count, negative_count, neutral_count, avg_score, source_dist):
    """Generate key metrics summary"""
    
    if total_records == 0:
        return html.Div("No metrics available.", className="text-muted")
    
    pos_pct = (positive_count / total_records * 100) if total_records > 0 else 0
    neg_pct = (negative_count / total_records * 100) if total_records > 0 else 0
    neu_pct = (neutral_count / total_records * 100) if total_records > 0 else 0
    
    metrics = [
        ("Total Records", str(total_records)),
        ("Positive Ratio", f"{pos_pct:.1f}%"),
        ("Negative Ratio", f"{neg_pct:.1f}%"),
        ("Neutral Ratio", f"{neu_pct:.1f}%"),
        ("Average Score", f"{avg_score:.3f}"),
        ("Data Sources", str(len(source_dist))),
        ("Sentiment Balance", "✅ Balanced" if 30 < pos_pct < 70 else "⚠️ Skewed"),
        ("Classification", "Reliable" if total_records > 100 else "Limited")
    ]
    
    metric_rows = []
    for metric_name, metric_value in metrics:
        metric_rows.append(
            html.Tr([
                html.Td(html.Strong(metric_name)),
                html.Td(html.Span(metric_value, className="badge badge-primary"))
            ])
        )
    
    return dbc.Table([
        html.Tbody(metric_rows)
    ], bordered=True, size="sm")


def generate_expected_vs_predicted(records):
    """Generate expected vs predicted sentiment analysis table"""
    
    if not records or len(records) == 0:
        return html.Div("No data available for comparison.", className="text-muted")
    
    # Group by sentiment and calculate confidence
    sentiment_groups = {'positive': [], 'negative': [], 'neutral': []}
    
    for record in records[:50]:  # Use latest 50 records
        sentiment = record.get('sentiment', 'unknown')
        if sentiment in sentiment_groups:
            sentiment_groups[sentiment].append(record)
    
    # Create comparison table
    table_rows = []
    
    for sentiment_type in ['positive', 'negative', 'neutral']:
        records_of_type = sentiment_groups[sentiment_type]
        
        if not records_of_type:
            continue
        
        count = len(records_of_type)
        avg_confidence = sum(r.get('confidence', 0) for r in records_of_type) / count if count > 0 else 0
        avg_score = sum(r.get('score', 0) for r in records_of_type) / count if count > 0 else 0
        
        # Determine accuracy badge
        if avg_confidence > 0.8:
            accuracy_badge = dbc.Badge("High", color="success")
        elif avg_confidence > 0.6:
            accuracy_badge = dbc.Badge("Medium", color="warning")
        else:
            accuracy_badge = dbc.Badge("Low", color="danger")
        
        # Format sentiment
        sentiment_colors = {
            'positive': 'success',
            'negative': 'danger',
            'neutral': 'warning'
        }
        sentiment_badge = dbc.Badge(sentiment_type.upper(), color=sentiment_colors.get(sentiment_type))
        
        table_rows.append(
            html.Tr([
                html.Td(sentiment_badge),
                html.Td(f"{count} samples"),
                html.Td(f"{avg_confidence:.1%}"),
                html.Td(f"{avg_score:.3f}"),
                html.Td(accuracy_badge)
            ])
        )
    
    # Add summary row
    total_samples = len(records[:50])
    all_confidence = sum(r.get('confidence', 0) for r in records[:50]) / total_samples if total_samples > 0 else 0
    
    table_rows.append(
        html.Tr([
            html.Td(html.Strong("Overall Average")),
            html.Td(html.Strong(f"{total_samples} samples")),
            html.Td(html.Strong(f"{all_confidence:.1%}")),
            html.Td("-"),
            html.Td(dbc.Badge("Summary", color="info"))
        ], className="table-active")
    )
    
    return dbc.Table([
        html.Thead(html.Tr([
            html.Th("Sentiment", style={'width': '15%'}),
            html.Th("Sample Count", style={'width': '20%'}),
            html.Th("Avg Confidence", style={'width': '20%'}),
            html.Th("Avg Score", style={'width': '20%'}),
            html.Th("Accuracy", style={'width': '15%'})
        ])),
        html.Tbody(table_rows)
    ], bordered=True, hover=True, responsive=True, striped=True)


# Callbacks
@app.callback(
    [Output('total-records', 'children'),
     Output('avg-score', 'children'),
     Output('positive-count', 'children'),
     Output('negative-count', 'children'),
     Output('sentiment-pie-chart', 'figure'),
     Output('source-bar-chart', 'figure'),
     Output('sentiment-timeline', 'figure'),
     Output('recent-sentiments-table', 'children'),
     Output('insights-comments', 'children'),
     Output('key-metrics', 'children'),
     Output('expected-predicted-table', 'children'),
     Output('last-sync-time', 'children'),
     Output('last-refresh-time', 'children')],
    [Input('interval-component', 'n_intervals'),
     Input('timerange-dropdown', 'value')]
)
def update_dashboard(n, timerange):
    """Update all dashboard components"""
    try:
        # Fetch statistics
        stats_response = requests.get(f"{API_URL}/api/stats?timerange={timerange}")
        stats = stats_response.json()
        
        # Fetch recent sentiments - get more to ensure fresh data
        sentiments_response = requests.get(f"{API_URL}/api/sentiments?limit=100")
        sentiments_data = sentiments_response.json()
        records = sentiments_data.get('records', [])
        
        # Sort by timestamp descending to show newest first
        records.sort(key=lambda x: x.get('timestamp', ''), reverse=True)
        
        # Extract stats
        total_records = stats.get('total_records', 0)
        avg_score = stats.get('average_score', 0)
        sentiment_dist = stats.get('sentiment_distribution', {})
        source_dist = stats.get('source_distribution', {})
        
        positive_count = sentiment_dist.get('positive', 0)
        negative_count = sentiment_dist.get('negative', 0)
        neutral_count = sentiment_dist.get('neutral', 0)
        
        # Sentiment pie chart
        pie_fig = go.Figure(data=[go.Pie(
            labels=['Positive', 'Negative', 'Neutral'],
            values=[positive_count, negative_count, neutral_count],
            marker=dict(colors=['#28a745', '#dc3545', '#ffc107'])
        )])
        pie_fig.update_layout(showlegend=True, height=300)
        
        # Source bar chart
        bar_fig = go.Figure(data=[go.Bar(
            x=list(source_dist.keys()),
            y=list(source_dist.values()),
            marker_color='#007bff'
        )])
        bar_fig.update_layout(
            xaxis_title="Source",
            yaxis_title="Count",
            height=300
        )
        
        # Timeline chart
        if records:
            df_records = []
            for record in records:
                df_records.append({
                    'timestamp': record['timestamp'],
                    'sentiment': record['sentiment'],
                    'score': record['score']
                })
            
            # Group by hour and sentiment
            from collections import defaultdict
            timeline_data = defaultdict(lambda: {'positive': 0, 'negative': 0, 'neutral': 0})
            
            for record in df_records:
                timestamp = datetime.fromisoformat(record['timestamp'].replace('Z', '+00:00'))
                hour_key = timestamp.strftime('%Y-%m-%d %H:00')
                sentiment = record['sentiment']
                timeline_data[hour_key][sentiment] += 1
            
            # Create timeline figure
            timestamps = sorted(timeline_data.keys())
            positive_vals = [timeline_data[ts]['positive'] for ts in timestamps]
            negative_vals = [timeline_data[ts]['negative'] for ts in timestamps]
            neutral_vals = [timeline_data[ts]['neutral'] for ts in timestamps]
            
            timeline_fig = go.Figure()
            timeline_fig.add_trace(go.Scatter(
                x=timestamps, y=positive_vals, name='Positive',
                mode='lines+markers', line=dict(color='#28a745')
            ))
            timeline_fig.add_trace(go.Scatter(
                x=timestamps, y=negative_vals, name='Negative',
                mode='lines+markers', line=dict(color='#dc3545')
            ))
            timeline_fig.add_trace(go.Scatter(
                x=timestamps, y=neutral_vals, name='Neutral',
                mode='lines+markers', line=dict(color='#ffc107')
            ))
            timeline_fig.update_layout(
                xaxis_title="Time",
                yaxis_title="Count",
                height=400
            )
        else:
            timeline_fig = go.Figure()
            timeline_fig.update_layout(height=400)
        
        # Recent sentiments table
        table_rows = []
        for record in records[:10]:
            sentiment_badge = {
                'positive': 'success',
                'negative': 'danger',
                'neutral': 'warning'
            }.get(record['sentiment'], 'secondary')
            
            table_rows.append(
                html.Tr([
                    html.Td(record['text'][:100] + '...' if len(record['text']) > 100 else record['text']),
                    html.Td(dbc.Badge(record['sentiment'].upper(), color=sentiment_badge)),
                    html.Td(f"{record['score']:.3f}"),
                    html.Td(record['source']),
                    html.Td(datetime.fromisoformat(record['timestamp'].replace('Z', '+00:00')).strftime('%Y-%m-%d %H:%M'))
                ])
            )
        
        table = dbc.Table([
            html.Thead(html.Tr([
                html.Th("Text"),
                html.Th("Sentiment"),
                html.Th("Score"),
                html.Th("Source"),
                html.Th("Time")
            ])),
            html.Tbody(table_rows)
        ], bordered=True, hover=True, responsive=True, striped=True)
        
        # Get current time for display
        current_time = datetime.now()
        sync_time = f"Last Synced: {current_time.strftime('%Y-%m-%d %H:%M:%S')}"
        refresh_time = f"Auto-refreshing every 5 seconds"
        
        # Generate insights and comments
        insights_html = generate_insights(
            total_records, avg_score, positive_count, negative_count, neutral_count,
            sentiment_dist, source_dist
        )
        
        # Generate key metrics
        key_metrics_html = generate_key_metrics(
            total_records, positive_count, negative_count, neutral_count,
            avg_score, source_dist
        )
        
        # Generate expected vs predicted analysis
        expected_predicted_html = generate_expected_vs_predicted(records)
        
        return (
            str(total_records),
            f"{avg_score:.3f}",
            str(positive_count),
            str(negative_count),
            pie_fig,
            bar_fig,
            timeline_fig,
            table,
            insights_html,
            key_metrics_html,
            expected_predicted_html,
            sync_time,
            refresh_time
        )
        
    except Exception as e:
        import traceback
        print(f"\n{'='*70}")
        print(f"ERROR IN DASHBOARD CALLBACK:")
        print(f"{'='*70}")
        print(f"Error: {e}")
        print(f"Traceback:")
        traceback.print_exc()
        print(f"{'='*70}\n")
        
        current_time = datetime.now()
        empty_insights = html.Div("Unable to load insights at this time.", className="text-danger")
        empty_metrics = html.Div("Unable to load metrics at this time.", className="text-danger")
        empty_comparison = html.Div("No data available yet.", className="text-danger")
        return ("N/A", "N/A", "N/A", "N/A", go.Figure(), go.Figure(), go.Figure(), 
                html.Div("Error loading data"), 
                empty_insights,
                empty_metrics,
                empty_comparison,
                f"Last Synced: {current_time.strftime('%Y-%m-%d %H:%M:%S')}",
                "Auto-refreshing every 5 seconds")


# Comparison callbacks
@app.callback(
    [Output('comparison-data-store', 'data'),
     Output('comparison-status', 'children')],
    [Input('run-comparison-btn', 'n_clicks')],
    prevent_initial_call=True
)
def run_comparison_test(n_clicks):
    """Run comparison test between batch and stream processing"""
    if n_clicks is None:
        return {}, ""
    
    try:
        # Fetch sample data from API
        response = requests.get(f"{API_URL}/api/sentiments?limit=100")
        data = response.json()
        records = data.get('records', [])
        
        if not records:
            # Use sample texts if no records
            sample_texts = [
                "I absolutely love this product! It's amazing!",
                "This is terrible and disappointing.",
                "It's okay, nothing special.",
                "Best experience ever! Highly recommended!",
                "Worst service I've ever had.",
                "Great quality and fast delivery.",
                "Not worth the money at all.",
                "Exceeded all my expectations!",
                "Very poor customer service.",
                "Fantastic! Will buy again!"
            ] * 10  # 100 texts
        else:
            sample_texts = [r['text'] for r in records[:100]]
        
        # Run comparison
        comparison_results = comparison_framework.run_comparison(sample_texts)
        flow_data = comparison_framework.get_flow_chart_data()
        
        # Combine data
        full_data = {
            'comparison': comparison_results['comparison'],
            'flow': flow_data
        }
        
        status = dbc.Alert([
            html.H5("Comparison Complete!", className="alert-heading"),
            html.P(f"Processed {len(sample_texts)} texts"),
            html.Hr(),
            html.P(f"Winner: {comparison_results['comparison']['faster_method'].upper()} "
                   f"({comparison_results['comparison']['speed_improvement']}% faster)",
                   className="mb-0")
        ], color="success")
        
        return full_data, status
        
    except Exception as e:
        error_status = dbc.Alert(f"Error running comparison: {str(e)}", color="danger")
        return {}, error_status


@app.callback(
    [Output('batch-flow-chart', 'figure'),
     Output('stream-flow-chart', 'figure'),
     Output('throughput-comparison-chart', 'figure'),
     Output('latency-comparison-chart', 'figure'),
     Output('time-comparison-chart', 'figure'),
     Output('comparison-table', 'children')],
    [Input('comparison-data-store', 'data')]
)
def update_comparison_visualizations(data):
    """Update all comparison visualizations"""
    if not data or 'flow' not in data:
        # Return empty figures if no data
        empty_fig = go.Figure()
        empty_fig.update_layout(
            title="Run comparison test to see results",
            showlegend=False
        )
        return empty_fig, empty_fig, empty_fig, empty_fig, empty_fig, html.Div("No comparison data yet")
    
    try:
        flow_data = data['flow']
        comp_data = data.get('comparison', {})
        
        # Batch flow chart (Sankey diagram)
        batch_stages = flow_data['batch_flow']['stages']
        batch_fig = create_flow_chart(batch_stages, "Batch Processing Flow", "#007bff")
        
        # Stream flow chart
        stream_stages = flow_data['stream_flow']['stages']
        stream_fig = create_flow_chart(stream_stages, "Stream Processing Flow", "#28a745")
        
        # Throughput comparison
        throughput_fig = go.Figure()
        throughput_fig.add_trace(go.Bar(
            x=['Batch', 'Stream'],
            y=[comp_data.get('batch_throughput', 0), comp_data.get('stream_throughput', 0)],
            marker_color=['#007bff', '#28a745'],
            text=[f"{comp_data.get('batch_throughput', 0):.2f}", 
                  f"{comp_data.get('stream_throughput', 0):.2f}"],
            textposition='auto',
        ))
        throughput_fig.update_layout(
            title="Items Processed per Second",
            yaxis_title="Throughput (items/s)",
            height=300
        )
        
        # Latency comparison
        latency_fig = go.Figure()
        latency_fig.add_trace(go.Bar(
            x=['Batch', 'Stream'],
            y=[comp_data.get('batch_avg_latency', 0), comp_data.get('stream_avg_latency', 0)],
            marker_color=['#007bff', '#28a745'],
            text=[f"{comp_data.get('batch_avg_latency', 0):.2f}ms", 
                  f"{comp_data.get('stream_avg_latency', 0):.2f}ms"],
            textposition='auto',
        ))
        latency_fig.update_layout(
            title="Average Latency per Item",
            yaxis_title="Latency (ms)",
            height=300
        )
        
        # Total time comparison
        time_fig = go.Figure()
        time_fig.add_trace(go.Bar(
            x=['Batch', 'Stream'],
            y=[comp_data.get('batch_total_time', 0), comp_data.get('stream_total_time', 0)],
            marker_color=['#007bff', '#28a745'],
            text=[f"{comp_data.get('batch_total_time', 0):.2f}s", 
                  f"{comp_data.get('stream_total_time', 0):.2f}s"],
            textposition='auto',
        ))
        time_fig.update_layout(
            title="Total Processing Time",
            yaxis_title="Time (seconds)",
            height=300
        )
        
        # Comparison table
        comparison_table_data = flow_data['comparison_table']
        table_rows = []
        for row in comparison_table_data:
            table_rows.append(
                html.Tr([
                    html.Td(html.Strong(row['metric'])),
                    html.Td(row['batch']),
                    html.Td(row['stream'])
                ])
            )
        
        comparison_table = dbc.Table([
            html.Thead(html.Tr([
                html.Th("Metric"),
                html.Th("Batch Processing"),
                html.Th("Stream Processing")
            ])),
            html.Tbody(table_rows)
        ], bordered=True, hover=True, striped=True, responsive=True)
        
        return batch_fig, stream_fig, throughput_fig, latency_fig, time_fig, comparison_table
        
    except Exception as e:
        print(f"Error updating comparison visualizations: {e}")
        empty_fig = go.Figure()
        return empty_fig, empty_fig, empty_fig, empty_fig, empty_fig, html.Div(f"Error: {str(e)}")


def create_flow_chart(stages, title, color):
    """Create a flow chart visualization for processing stages"""
    # Create a funnel chart to represent the flow
    stage_names = [stage['name'] for stage in stages]
    stage_values = [stage['time_percent'] for stage in stages]
    stage_descriptions = [stage['description'] for stage in stages]
    
    fig = go.Figure()
    
    # Create horizontal bar chart representing flow
    fig.add_trace(go.Funnel(
        y=stage_names,
        x=stage_values,
        textinfo="label+percent initial",
        marker=dict(color=color),
        hovertemplate='<b>%{label}</b><br>Time: %{value}%<extra></extra>'
    ))
    
    fig.update_layout(
        title=title,
        height=400,
        showlegend=False
    )
    
    return fig


if __name__ == '__main__':
    port = int(os.getenv('DASHBOARD_PORT', 8050))
    app.run_server(debug=True, host='0.0.0.0', port=port)
