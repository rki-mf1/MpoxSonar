import dash
from dash import html, dcc

dash.register_page(__name__, path='/About')

layout = html.Div(
    children=[
        
        html.H1(children="Project Description"),
            html.Div(
                children="""
                        Monkeypox is an infectious disease caused by a smallpox virus, recently spreading in multiple countries with over 16,500 cases and declared a global emergency by the World Health Organization (citation). 
                        Normally, the virus is rarely observed outside of Africa, but in recent months it has occurred in over 11 countries in other continents [CITATION]. 
                        This alarming behavior demands action and highlights the need for genomic surveillance and spatio-temporal analyses. 
                        Therefore, the Robert Koch Institute (RKI) together with the Hasso Platter Institute (HPI) joined forces to and adapted the tool covSonar - a database framework developed at the RKI for SARS-CoV-2 - to Monkeypox.
                    """
             ),
        
        html.H1(children="Who are we?"),
            html.Img(src=r'https://upload.wikimedia.org/wikipedia/commons/9/99/Sample_User_Icon.png', alt='user', style={'height':'10%', 'width':'10%', 'display':'inline-block'}),
            html.Div('user1', style={'display':'inline-block'}),
            html.Img(src=r'https://upload.wikimedia.org/wikipedia/commons/9/99/Sample_User_Icon.png', alt='user', style={'height':'10%', 'width':'10%', 'display':'inline-block', "margin-left": "150px"}),
            html.Div('user1', style={'display':'inline-block'}),
            html.Img(src=r'https://upload.wikimedia.org/wikipedia/commons/9/99/Sample_User_Icon.png', alt='user', style={'height':'10%', 'width':'10%', 'display':'inline-block', "margin-left": "150px"}),
            html.Div('user1', style={'display':'inline-block'}),
            html.Br(),
            html.Img(src=r'https://upload.wikimedia.org/wikipedia/commons/9/99/Sample_User_Icon.png', alt='user',   ),
            html.Div('user1', style={'display':'inline-block'}),
            html.Img(src=r'https://upload.wikimedia.org/wikipedia/commons/9/99/Sample_User_Icon.png', alt='user', style={'height':'10%', 'width':'10%', 'display':'inline-block', "margin-left": "150px"}),
            html.Div('user1', style={'display':'inline-block'}),
            html.Img(src=r'https://upload.wikimedia.org/wikipedia/commons/9/99/Sample_User_Icon.png', alt='user', style={'height':'10%', 'width':'10%', 'display':'inline-block', "margin-left": "150px"}),
            html.Div('user1', style={'display':'inline-block'}),
            html.Br(),
            html.Img(src=r'https://upload.wikimedia.org/wikipedia/commons/9/99/Sample_User_Icon.png', alt='user', style={'height':'10%', 'width':'10%', 'display':'inline-block'}),
            html.Div('user1', style={'display':'inline-block'}),
            html.Img(src=r'https://upload.wikimedia.org/wikipedia/commons/9/99/Sample_User_Icon.png', alt='user', style={'height':'10%', 'width':'10%', 'display':'inline-block', "margin-left": "150px"}),
            html.Div('user1', style={'display':'inline-block'}),
            html.Img(src=r'https://upload.wikimedia.org/wikipedia/commons/9/99/Sample_User_Icon.png', alt='user', style={'height':'10%', 'width':'10%', 'display':'inline-block', "margin-left": "150px"}),
            html.Div('user1', style={'display':'inline-block'}),
            html.Br(),
                
        html.H1(children="What is a mutation?"),
            html.Div(
                children="""
                        ...
                    """
            ),
                        
        html.H1(children="Data sources"),
            html.Div(
                children="""
                        ...
                    """
            ),
                        
        html.H1(children="Link to code:"),
            html.Div(
                children="""
                        ...
                    """
            ),
                        
        html.H1(children="Acknowledgements:"),
            html.Div(
                children="""
                        ...
                    """
            ),
    ]
)
