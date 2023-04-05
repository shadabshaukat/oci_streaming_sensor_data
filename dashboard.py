import dash
from dash import dcc
from dash import html
from dash.dependencies import Input, Output
import plotly.graph_objs as go
import oracledb
import pandas as pd
import sqlalchemy as sa
from datetime import datetime, timedelta
import sys

oracledb.version = "8.3.0"
sys.modules["cx_Oracle"] = oracledb

# Oracle Database credentials
oracle_un = 'admin'
oracle_pw = 'RAbbithole1234#_'
oracle_cs = '(description= (retry_count=20)(retry_delay=3)(address=(protocol=tcps)(port=1521)(host=adb.ap-melbourne-1.oraclecloud.com))(connect_data=(service_name=g9b8049aad9c64c_y16fuv7vqq9428l5_high.adb.oraclecloud.com))(security=(ssl_server_dn_match=yes)))'

connection = oracledb.connect(user=oracle_un, password=oracle_pw, dsn=oracle_cs)

oracle_engine = sa.create_engine(f'oracle://{oracle_un}:{oracle_pw}@{oracle_cs}')
last_n_minutes = 1440

# Group the Sensors
group1_sensors = ['s001', 's002', 's003', 's004', 's005']

selected_group = group1_sensors

app = dash.Dash(__name__)

app.layout = html.Div(
    children=[
        html.H1(children='Sensor Data (Temperature & Humidity)'),
        dcc.Graph(id='live-graph', animate=True),
        dcc.Interval(
            id='graph-update',
            interval=60 * 1000,  # Update every 60 seconds
            n_intervals=0
        ),
    ]
)

def get_sensor_data():
    global oracle_engine
    global last_n_minutes
    filter_timestamp = datetime.utcnow() - timedelta(minutes=last_n_minutes)
    query = f"SELECT * FROM sensor_data WHERE timestamp >= TO_DATE('{filter_timestamp.strftime('%Y-%m-%dT%H:%M:%S')}', 'YYYY-MM-DD\"T\"HH24:MI:SS')"
    df = pd.read_sql(query, con=oracle_engine)
    df['timestamp'] = pd.to_datetime(df['timestamp'], utc=True).dt.tz_convert(None)
    return df

def detect_anomalies(sensor_df, window=20, num_std_dev=2):
    anomalies = []

    for sensor_id in sensor_df['sensor_id'].unique():
        sensor_data = sensor_df[sensor_df['sensor_id'] == sensor_id]

        sensor_data['rolling_temp_std'] = sensor_data['temperature'].rolling(window=window).std()
        sensor_data['rolling_hum_std'] = sensor_data['humidity'].rolling(window=window).std()

        sensor_data['rolling_temp_mean'] = sensor_data['temperature'].rolling(window=window).mean()
        sensor_data['rolling_hum_mean'] = sensor_data['humidity'].rolling(window=window).mean()

        temp_anomaly = sensor_data[(sensor_data['temperature'] > sensor_data['rolling_temp_mean'] + num_std_dev * sensor_data['rolling_temp_std']) |
                                   (sensor_data['temperature'] < sensor_data['rolling_temp_mean'] - num_std_dev * sensor_data['rolling_temp_std'])]
        hum_anomaly = sensor_data[(sensor_data['humidity'] > sensor_data['rolling_hum_mean'] + num_std_dev * sensor_data['rolling_hum_std']) |
                                  (sensor_data['humidity'] < sensor_data['rolling_hum_mean'] - num_std_dev * sensor_data['rolling_hum_std'])]

        anomalies.extend(temp_anomaly.to_dict('records'))
        anomalies.extend(hum_anomaly.to_dict('records'))

    return anomalies


@app.callback(Output('live-graph', 'figure'),
              Input('graph-update', 'n_intervals'))
def update_graph_live(n):
    global oracle_engine
    global last_n_minutes

    # Filter data based on the last N minutes
    filter_timestamp = datetime.utcnow() - timedelta(minutes=last_n_minutes)
    query = f"SELECT * FROM sensor_data WHERE timestamp >= TO_DATE('{filter_timestamp.strftime('%Y-%m-%dT%H:%M:%S')}', 'YYYY-MM-DD\"T\"HH24:MI:SS')"

    df = pd.read_sql(query, con=oracle_engine)
    df['timestamp'] = pd.to_datetime(df['timestamp'], utc=True).dt.tz_convert(None)

    fig = go.Figure()

    for sensor_id in df['sensor_id'].unique():
        if sensor_id not in selected_group:
            continue

        sensor_df = df[df['sensor_id'] == sensor_id]

        fig.add_trace(go.Scatter(
            x=sensor_df['timestamp'],
            y=sensor_df['temperature'],
            mode='markers',
            marker=dict(size=6),
            name=f'Temperature ({sensor_id})'
        ))

        fig.add_trace(go.Scatter(
            x=sensor_df['timestamp'],
            y=sensor_df['humidity'],
            mode='markers',
            marker=dict(size=6),
            name=f'Humidity ({sensor_id})'
        ))

        anomalies = detect_anomalies(sensor_df)
        for anomaly in anomalies:
            if 'temperature' in anomaly:
                fig.add_trace(go.Scatter(
                    x=[anomaly['timestamp']],
                    y=[anomaly['temperature']],
                    mode='markers',
                    marker=dict(size=8, color='red'),
                    name='Temperature Anomaly',
                    hovertext=f"Anomaly Detected in Sensor {sensor_id} on Temperature",
                    showlegend=False
                ))
            if 'humidity' in anomaly:
                fig.add_trace(go.Scatter(
                    x=[anomaly['timestamp']],
                    y=[anomaly['humidity']],
                    mode='markers',
                    marker=dict(size=8, color='red'),
                    name='Humidity Anomaly',
                    hovertext=f"Anomaly Detected in Sensor {sensor_id} on Humidity",
                    showlegend=False
                ))

    fig.update_layout(
        title='Sensor Data (Temperature & Humidity)',
        xaxis=dict(
            title='Timestamp',
            type='date',
            tickformat='%Y-%m-%dT%H:%M:%S',
            rangeslider=dict(
                visible=True,
                autorange=True,
            ),
        ),
        yaxis=dict(
            title='Temperature / Humidity'
        )
    )

    return fig


if __name__ == '__main__':
    app.run_server(debug=True)
