# define a function to process the ingested csv file
def process_csv(data): 
    import pandas as pd
    # subset the data for manipulation
    data2 = data.iloc[1:, 0:8]
    
    # rename the columns
    data2.columns = ['Order_ID','Order_Date','Status','Lab','Package','User','Type','Number_Samples']

    # removed columns not used in analysis
    data4 = data2.drop(columns=['Status', 'Lab', 'Package', 'Type'], axis=1)
    
    # exclude data with missing value
    data4.dropna(inplace=True)
    
    # extract the user name
    data4['User'] = data4['User'].apply(lambda x: x.split(' (')[0])
    
    # convert the order_date into datetime format
    data4['Order_Date'] = pd.to_datetime(data4['Order_Date'], format='%Y-%m-%d', errors='coerce')
    
    fil = data4[data4['Order_Date'].isna()]
    data5 = data4.drop(index=fil.index.tolist())
    
    data5['Order_Date'] = data5['Order_Date'].dt.strftime('%Y-%m-%d')
    data5['Order_ID'] = data5['Order_ID'].str.strip(' ')
    return data5


# function to get key metrics
def get_key_metrics(data):
    import pandas as pd
    total_expenses = round(data['Number_Samples'].sum() * 4.6, 2)
    monthly_average = round(total_expenses/12, 2)
    daily_average = round(total_expenses / 365, 2)
    total_orders = data.shape[0]
    total_rxn = data['Number_Samples'].sum()
    avg_rxn_per_oder = round(total_rxn/total_orders,2)
    number_of_users = data['User'].nunique()    
    return [total_expenses, monthly_average, daily_average, total_orders, total_rxn, avg_rxn_per_oder, number_of_users]

# function to plot donut chart
def plot_donut(selected_year_exp, total_exp):
    import plotly.graph_objects as go
    # specify colors
    colors = ['#fa9c3c', '#FF6347']  

    fig = go.Figure(data=[go.Pie(labels=['Selected_year', 'Other Years'],
                                values=[selected_year_exp, total_exp - selected_year_exp],
                                hole=.5, marker=dict(colors=colors), textfont=dict(size=18))])
    fig.update_layout(height=500, margin = dict(t=30, l=25, r=25, b=25))
    fig.update_layout(showlegend=False)
    return fig


# function to preprocess the data for plotting heatmap
def preprocess_heatmap(data):
    import pandas as pd
    import numpy as np

    daily_total = data.groupby(['Year','Month','Day'])['Number_Samples'].sum().reset_index()
    
    years = daily_total['Year'].unique()
    months = daily_total['Month'].unique()
    days = np.arange(1,32)

    index = pd.MultiIndex.from_product([years, months, days], names = ['Year','Month', 'Day'])

    daily_total = daily_total.set_index(['Year','Month', 'Day']).reindex(index, fill_value=0).reset_index()
    return daily_total


# function to plot heatmap
def plot_heatmap(data, year):
    import pandas as pd
    import plotly.graph_objects as go
    
    selected_data = data[data['Year'] == year]
    pivot = selected_data.pivot(index='Month', columns='Day', values='Number_Samples').fillna(0)

    # create the heatmap using Plotly Graph Objects
    fig = go.Figure(data=go.Heatmap(
        z=pivot.values,
        x=pivot.columns,
        y=pivot.index,
        colorscale='sunset_r',
        #colorbar=dict(title='Number of Reactions'),
        hovertemplate='Month: %{y}<br>Day: %{x}<br>Number of Reactions: %{customdata}<extra></extra>',
        customdata=pivot.values
    ))

    # add border lines by drawing rectangles around each cell
    shapes = []
    for i, row in enumerate(pivot.index):
        for j, col in enumerate(pivot.columns):
            shapes.append(
                go.layout.Shape(
                    type="rect",
                    x0=col - 0.5, x1=col + 0.5,
                    y0=row - 0.5, y1=row + 0.5,
                    line=dict(color='grey', width=1)
                )
            )

    fig.update_layout(
        #title=f'Number of Samples Sequenced in {year}',
        xaxis_title='Day',
        #yaxis_title='Month',
        xaxis=dict(
            tickmode='array',
            tickvals=list(range(1, 32)),
        ),
        yaxis=dict(
            tickmode='array',
            tickvals=pivot.index.tolist(),
            ticktext=['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
        ),
        shapes=shapes,
        height=500,
        width=1200,
        template='plotly_dark'
    )

    fig.update_layout(margin = dict(t=20, l=25, r=25, b=25))
    return fig


# function to plot bubble chart
def plot_bubble(data, year):
    import plotly.express as px
    import pandas as pd
    
    # remove the negative value in the data
    df = data[data['Number_Samples'] > 0]

    # aggregate the data by summing the 'Value' for each 'Vendor' and 'Category' combination
    aggregated_data = df.groupby(['Month', 'User']).agg({'Number_Samples': 'sum'}).reset_index()

    # create the bubble chart using the aggregated data
    fig = px.scatter(
        aggregated_data, 
        x='Month', 
        y='Number_Samples', 
        size='Number_Samples',  # column to determine the size of the bubbles
        color='User', 
        size_max=60, 
        height=1100,
        width=500,
    )

    fig.update_layout(template='plotly_dark',
                      legend=dict(orientation='h',
                                  yanchor='bottom',
                                  y=-0.2,
                                  xanchor='center',
                                  x=0.5),
            xaxis=dict(
            tickmode='array',
            tickvals=df['Month'].unique().tolist(),
            ticktext=['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
        ))
    return fig


def plot_bubble2(data, year):
    import plotly.express as px
    import pandas as pd

    # define all months
    all_months = pd.DataFrame({
        'Month': range(1, 13),
        'Month_Name': ['January', 'February', 'March', 'April', 'May', 'June',
                       'July', 'August', 'September', 'October', 'November', 'December']
    })

    # Remove the negative value in the data
    df = data[data['Number_Samples'] > 0]

    # Aggregate the data by summing the 'Number_Samples' for each 'Month' and 'User' combination
    aggregated_data = df.groupby(['Month', 'User']).agg({'Number_Samples': 'sum'}).reset_index()

    # Merge with all_months to include missing months
    all_users = aggregated_data['User'].unique()
    full_data = pd.DataFrame()

    for user in all_users:
        user_data = pd.merge(all_months, aggregated_data[aggregated_data['User'] == user], on='Month', how='left')
        user_data['User'] = user
        user_data['Number_Samples'].fillna(0, inplace=True)
        full_data = pd.concat([full_data, user_data])

    # Create the bubble chart using the full data
    fig = px.scatter(
        full_data,
        x='Month_Name',
        y='Number_Samples',
        size='Number_Samples',
        color='User',
        size_max=60,
        height=1100,
        width=500,
    )

    fig.update_layout(template='plotly_dark',
                      xaxis_title='',
                      legend=dict(orientation='h',
                                  yanchor='bottom',
                                  y=-0.2,
                                  xanchor='center',
                                  x=0.5,
                                  font=dict(size=18)))
    return fig



# function to plot bar chart
def plot_bar(data, year):
    import plotly.graph_objects as go
    import pandas as pd

    # list of all months
    all_months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    month_numbers = list(range(1, 13))  # Corresponding month numbers 1 to 12

    # create a DataFrame to ensure all months are included
    full_months_df = pd.DataFrame({
        'Month': month_numbers,
        'Month_Name': all_months
    })

    # group by month and sum the number of samples
    monthly_usage = data.groupby('Month')['Number_Samples'].sum().reset_index()

    # Merge to ensure all months are included
    df = pd.merge(full_months_df, monthly_usage, on='Month', how='left').fillna(0)

    # Create the bar plot with a specified color
    fig = go.Figure(data=[go.Bar(x=df['Month_Name'], y=df['Number_Samples'], marker_color='#fa9c3c')])

    # Update layout
    fig.update_layout(
        height=500,
        #xaxis_title='Month',
        yaxis_title='Number of Reactions',
        xaxis=dict(
            tickmode='array',
            tickvals=all_months,
            ticktext=all_months
        ),
        template='plotly_dark'
    )

    fig.update_layout(margin = dict(t=10, l=20, r=20, b=20))

    return fig
