import dash_bootstrap_components as dbc
import dash
from dash import html, dcc

dash.register_page(__name__, path="/Help")


table_header = [
    html.Thead(html.Tr([html.Th("OS"), html.Th("Version"), html.Th(
        "Chrome"), html.Th("Firefox"), html.Th("Microsoft Edge"), html.Th("Safari")]))
]

row1 = html.Tr([html.Td("Linux"), html.Td("CentOS 7"), html.Td(
    "Not tested"), html.Td("61. 0"), html.Td("n/a"), html.Td("n/a")])
row2 = html.Tr([html.Td("MacOS"), html.Td("HighSierra"), html.Td(
    "Not tested"), html.Td("61. 0"), html.Td("n/a"), html.Td("12.0")])
row3 = html.Tr([html.Td("10"), html.Td("10"), html.Td("Not tested"),
               html.Td("61. 0"), html.Td("42.17134.1.0"), html.Td("n/a")])

table_body = [html.Tbody([row1, row2, row3])]

table = dbc.Table(table_header + table_body, bordered=True)


layout = html.Div(
    children=[
        html.H2(children="MPoxRadar Help Page:", style={'textAlign': 'center'}),
        html.Div(
            children="""
                MPoxRadar is a website visualising the distribution of MonkeyPox mutations and allowing the user to filter which information they are interested in having visualised. The website also allows the download of the selected filter of information. In the following section you will see an explanation for each functionality and section of the “Tool” page of our website. Followed by a section dedicated to answering frequently asked questions (FAQ) and a description of the tested browser compatibility of our website.
            """, style={'textAlign': 'center'}),

        html.Br(),

        html.Div(
            children="""
                Functionalities from MPoxRadar explained:
            """, style={"margin-left": '10px'}
        ),
        html.Img(src="assets/example_ReferenceGenome.png",
                 style={'float': 'right', "width": "100%", "max-width": "200px", "height": "auto"}),
        html.Ul([html.Li([html.Strong("Reference genomes:")],
                style={"margin-left": '10px'}),
            html.Ul([html.Li([html.Div("""
                                       Here you see a list of reference genomes to choose from. As MonkeyPox has no unanimously defined reference genome (given its widespread and different clusters), we allow users to choose a reference genome from which the mutations will be calculated from.""")]),
                     html.Li(
                         ["There are currently three options available for this field:"]),
                     html.Ul([html.Li([html.Strong("NC_063383.1"), """ This genome is one of the reference genomes pointed out by the National Center for Biotechnology Information
                     """, "(", dcc.Link(html.A("NCBI"), href="https://www.ncbi.nlm.nih.gov/, target='_blank'"), "): ", dcc.Link(href="https://www.ncbi.nlm.nih.gov/genomes/GenomesGroup.cgi?taxid=10244", target='_blank'), "."
                                       ]),
                              html.Li([html.Strong("ON563414.1"), """ USA Center for Disease Control sequence (as stated
                     """, "(", dcc.Link(html.A("here"), href="https://labs.epi2me.io/basic-monkeypox-workflow/#workflow-steps, target='_blank'"), "). "
                                       ]),
                              html.Li([html.Strong("MT903344.1"), """ Monkeypox virus isolate MPXV-UK_P2 (as stated
                     """, "(", dcc.Link(html.A("here"), href="https://labs.epi2me.io/basic-monkeypox-workflow/#workflow-steps, target='_blank'"), "). "
                                       ]),
                              ]),
                     html.Li(
                         "The user can choose exactly one reference genome from this list for the further steps. "),
                     html.Li("The default reference genome is NC_063383.1"),
                     ]),

            html.Img(src="assets/example_MutationsDisplayed.png",
                         style={'float': 'right', "width": "100%", "max-width": "200px", "height": "auto"}),
            html.Li(html.Strong("Mutations:")),
            html.Ul([
                html.Li(
                    ["After choosing one reference genome, this list will be updated with the available list of mutations."]),
                html.Li(
                    ["The user can choose as many mutations from the list as they like to have visualised on the plot. "]),
                html.Li(["In order to allow for easy access to choosing all mutations, there is always an option to choose “", html.Strong(
                    "all"), "”, which is also the option chosen by default."]),
            ]),
            html.Li(
                ["After choosing a reference genome, the ", html.Strong("list of Mutations"), " will be displayed for the user to choose from."]),
            html.Li(["There is a list of ", html.Strong("visualisation methods"),
                    ", since visualising a trend arrow on the map is more complicated, we decided to have the trend be a visualising option instead."]),
            html.Li([html.Strong("Sequencing Technologies"),
                    " can furthermore be chosen from a list."]),
            html.Li(["Users can also directly give in a ", html.Strong("query using the MPXSonar notation"),
                    ". This text should be parsed and checked before being passed to the database to avoid security leaks."]),
            html.Li(["The ", html.Strong(
                "map"), " will then use the chosen visualisation method and visualise the mutations chosen for the time period selected."]),
            html.Li(["Users can press the “", html.Strong("Play animation"),
                    "” button to see the visualisations one after the other from a certain date. This video could also be downloaded as a gif using the “", html.Strong("Download animation as GIF” button"), "."]),
            html.Li(["Furthermore, the query results can be shown as a table by pressing the “Show results in a table” button. Here, we need to be careful not to show all results if the table is too large, as to not overwhelm the user's memory or crash the website."]),
            html.Li(
                ["The result should also be downloadable using the button “", html.Strong("Download results as a csv file"), "”."]),
            html.Li(["A brief explanation of each field on top needs to be added to the ", html.Strong("“i” button"),
                    ". For the “direct MPXSonar query input”, this could be a sentence linking to the MPXSonar documentation which explains what each tag is and how to use it."]),
        ]),

        html.H3(
            children="""
                FAQ:
            """
        ),
        html.Div(
            children="""
                What is genome?
            """
        ),
        html.Li(
            children="""
                A genome is all the genetic information of an organism. It consists of nucleotide sequences of DNA (or RNA in RNA viruses) in an organism. In people, almost every cell in the body contains a complete copy of the genome. The genome contains all of the information needed for a person to develop and grow. 
            """
        ),
        html.Br(),
        html.Div(
            children="""
                What is a mutation?
            """
        ),
        html.Li(
            children="""
                A mutation is a change in the genetic code, which is caused by errors in replication. These changes can lead to a change in nucleotides, which in turn can lead to changes in amino acids. Amino acids form proteins and these have a variety of functions in the organism. 
            """
        ),
        html.Br(),
        html.Div(
            children="""
                Why do we have multiple references? What changes when you change the reference?
            """
        ),
        html.Div(
            children="""
                ...
            """
        ),
        html.Br(),
        html.Div(
            children="""
                What is the difference between a nucleotide and amino acid?
            """
        ),
        html.Li(
            children="""
                A nucleotide is a unit that makes up a nucleic acid. Nucleotide names are indicated by a four-letter code: Adenine(A), Cytosine(C), Thymine(T), Guanine(G). And the polymer of nucleotides is RNA. When three consecutive nucleotide units come together, it is called a codon, and this codon structure represents the 20 amino acids that make up a protein.

            """
        ),
        html.Br(),
        html.Div(
            children="""
                How often it gets updated?
            """
        ),
        html.Div(
            children="""
                ...
            """
        ),
        html.Br(),
        html.H4(
            children="""
                Browser compatibility
            """
        ),
        dbc.Table(table)
    ],
),
