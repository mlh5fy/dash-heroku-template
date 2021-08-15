import numpy as np
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import plotly.graph_objects as go
import plotly.figure_factory as ff
import dash
from jupyter_dash import JupyterDash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']


%%capture
gss = pd.read_csv("https://github.com/jkropko/DS-6001/raw/master/localdata/gss2018.csv",
                 encoding='cp1252', na_values=['IAP','IAP,DK,NA,uncodeable', 'NOT SURE',
                                               'DK', 'IAP, DK, NA, uncodeable', '.a', "CAN'T CHOOSE"])

mycols = ['id', 'wtss', 'sex', 'educ', 'region', 'age', 'coninc',
          'prestg10', 'mapres10', 'papres10', 'sei10', 'satjob',
          'fechld', 'fefam', 'fepol', 'fepresch', 'meovrwrk'] 
gss_clean = gss[mycols]
gss_clean = gss_clean.rename({'wtss':'weight', 
                              'educ':'education', 
                              'coninc':'income', 
                              'prestg10':'job_prestige',
                              'mapres10':'mother_job_prestige', 
                              'papres10':'father_job_prestige', 
                              'sei10':'socioeconomic_index', 
                              'fechld':'relationship', 
                              'fefam':'male_breadwinner', 
                              'fehire':'hire_women', 
                              'fejobaff':'preference_hire_women', 
                              'fepol':'men_bettersuited', 
                              'fepresch':'child_suffer',
                              'meovrwrk':'men_overwork'},axis=1)
gss_clean.age = gss_clean.age.replace({'89 or older':'89'})
gss_clean.age = gss_clean.age.astype('float')

markdown_text2 = '''
    Many studies have been conducted to explore the difference in income between men and women, 
    and the overall consensus is that women consistently make less income than men. Despite the 
    Equal Pay Act being signed in 1963, a woman working full-time and year-round still only makes 
    84 cents to every dollar her male-counterpart makes. What is even more discouraging is that 
    based on the rate at which the pay gap is narrowing, women will not receive equal pay until 2059.
    Some big factors in the gender wage gap are over-representation of women in lower income jobs, 
    gender discrimination in the workplace, parenthood shifting the career path of a women, and more. 
      
      
    The General Social Survey explores social issues in the United States by collecting data on a 
    representative sample of individuals. The GSS collects their data through a personal-interview 
    survey where they ask participants questions about social issues to analyze their opinions, 
    attitudes, and behaviors.
      
      
    This document will look at several social factors compared by gender to further analyze the 
    gender wage gap.
'''

citation = '''
    https://www.americanprogress.org/issues/women/reports/2020/03/24/482141/quick-facts-gender-wage-gap/
    
    https://www.pay-equity.org/info-time.html
    
    https://www.pewresearch.org/fact-tank/2021/05/25/gender-pay-gap-facts/
    
    http://www.gss.norc.org/About-The-GSS
'''


gss_tab = gss_clean.groupby('sex').agg({'income':'mean','job_prestige':'mean','socioeconomic_index':'mean','education':'mean'})
gss_tab.rename(columns={'income':'Income', 'job_prestige': 'Occupational Prestige', 
                        'socioeconomic_index':'Socioeconomic Status', 'education':'Education'}, inplace=True)
gss_tab['Income'] = round(gss_tab['Income'],2)
gss_tab['Occupational Prestige'] = round(gss_tab['Occupational Prestige'],2)
gss_tab['Socioeconomic Status'] = round(gss_tab['Socioeconomic Status'],2)
gss_tab['Education'] = round(gss_tab['Education'],2)
gss_tab = gss_tab.reset_index()
table = ff.create_table(gss_tab)

gss_bar = gss_clean.groupby(['male_breadwinner', 'sex']).agg({'id':'count'}).reset_index()
bar = px.bar(gss_bar, y='id', x='male_breadwinner', color='sex',
            labels={'male_breadwinner':'Level of Agreement', 'id':'Count'},
            barmode='group')
bar.update_layout(showlegend=False)
bar.update(layout=dict(title=dict(x=0.5)))

scatter = px.scatter(gss_clean, x='job_prestige', y='income',color='sex',
                 trendline='ols',
                 height=600, width=600,
                 labels={'job_prestige':'Occupational Prestige', 
                        'income':'Income'},
                 hover_data=['education', 'socioeconomic_index'])
scatter.update(layout=dict(title=dict(x=0.5)))


box1 = px.box(gss_clean, x='sex', y = 'income', color = 'sex',
                   labels={'sex':'', 'income':'Income'})
box1.update_layout(showlegend=False)
box1.update(layout=dict(title=dict(x=0.5)))

box2 = px.box(gss_clean, x='sex', y = 'job_prestige', color = 'sex',
                   labels={'sex':'', 'job_prestige':'Occupational Prestige'})
box2.update_layout(showlegend=False)
box2.update(layout=dict(title=dict(x=0.5)))

new_gss = gss_clean[['income', 'sex', 'job_prestige']]
low = min(new_gss['job_prestige'])-1
up = max(new_gss['job_prestige'])
jump = (up-low)/7
new_gss['job_prestige'] = pd.cut(new_gss.job_prestige, np.arange(low, up, jump),
                                labels = ['group 1', 'group 2', 'group 3', 'group 4', 'group 5', 'group 6'])
new_gss = new_gss.dropna().sort_values('job_prestige')

box_facet = px.box(new_gss, x='income', y='sex', color='sex', 
             facet_col='job_prestige', facet_col_wrap=2,
             hover_data = ['job_prestige', 'sex', 'income'],
            labels={'job_prestige':'Occupational Prestige', 'income':'Income', 'sex':'Sex'},
             color_discrete_map = {'male':'blue', 'female':'red'})
box_facet.update(layout=dict(title=dict(x=0.5)))
box_facet.update_layout(showlegend=True)

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
colors = {
    'background': '#C2E6EF',
    'text': '#000000'}
app.layout = html.Div(style={'backgroundColor': colors['background']}, children=[
        
        dcc.Tabs(id='tabs-example', value='tab-1', children=[
            dcc.Tab(label='Overview', value='tab-1'),
            dcc.Tab(label='Initial Comparison', value='tab-2'),
            dcc.Tab(label='Analysis by Sex', value='tab-3')
        ]),
        
        html.Div(id='tabs-example-content')
    ]
)

@app.callback(Output('tabs-example-content', 'children'),
              Input('tabs-example', 'value'))

def render_content(tab):
    if tab == 'tab-1':
        return html.Div([
            html.H1("Exploring the Gender Pay Gap"),
            
            html.H2("What is the Gender Pay Gap and the GSS?"),
            dcc.Markdown(children = markdown_text2, style={
                'padding': '15px 30px 27px',
                'margin': '45px auto 45px',
                'width': '80%',
                'max-width': '1024px',
                'borderRadius': 5,
                'border': 'thin darkgrey solid',
                'font-family': 'Roboto, sans-serif'
            }),
            html.Cite(children=citation)
        ])
    elif tab == 'tab-2':
        statements = ['satjob', 'relationship', 'male_breadwinner', 'men_bettersuited', 'child_suffer', 'men_overwork']
        groups = ['sex', 'region', 'education']
        return html.Div([

            
            html.H2('Table Comparison by Sex'),
            html.H4('Looking at Mean Income, Occupational Prestige, Socioeconomic Status, and Education'),
            dcc.Graph(figure=table), 
            
            html.H2('Interactive Bar Plot'),
            html.H4('Level of Agreement with Various Statements by Sex, Region, or Education'),
            
            
            html.Div([
                html.H5("x-axis feature"),
            
                dcc.Dropdown(id='x-axis', options=[{'label': i, 'value': i} for i in statements], value='male_breadwinner'),
                
                html.H5("colors"),
            
                dcc.Dropdown(id='color',options=[{'label': i, 'value': i} for i in groups], value='sex')
                
            ], style={'width': '25%', 'float': 'left'}),
            

            
            html.Div([dcc.Graph(id="graph", style={"width":"70%", "display":"inline-block"})])
        ])
    elif tab == 'tab-3':

        return html.Div([
            html.H2("Income Against Occupational Prestige, by Sex"),
            dcc.Graph(figure=scatter),
            
            html.Div([
                html.H2("Income by Sex"),
                dcc.Graph(figure=box1)
            ], style = {'width':'49%', 'float':'left'}),
        
            html.Div([
                html.H2("Occupational Prestige by Sex"),
                dcc.Graph(figure=box2)
            ], style = {'width':'49%', 'float':'right'}),
        
            html.H2("Income by Sex, by Occupational Prestige Group"),

            dcc.Graph(figure = box_facet)
            
        ])

@app.callback(Output(component_id="graph",component_property="figure"), 
             [Input(component_id='x-axis',component_property="value"),
              Input(component_id='color',component_property="value")])

def make_figure(x, color):
    gss_bar = gss_clean.groupby([x, color]).agg({'id':'count'}).reset_index()
    mybar = px.bar(gss_bar, y='id', x=x, color=color, barmode='group')
    mybar.update(layout=dict(title=dict(x=0.5)))
    return mybar

if __name__ == '__main__':
    app.run_server(debug=True)
