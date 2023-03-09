from viktor import ViktorController
from viktor.parametrization import ViktorParametrization, TextField, IntegerField, TextAreaField, FileField, ActionButton, GeoPointField, OptionField, DateField
from viktor.views import PlotlyView, PlotlyResult, MapView, MapResult, MapPoint
import plotly.graph_objects as go
import csv
import pandas as pd

class Parametrization(ViktorParametrization):
    asset_name          = TextField("Assetnaam")
    asset_brand         = TextField("Merk")
    serial_number       = IntegerField("Serienummer")
    buy_year            = DateField("Bouwjaar")
    on_year             = DateField("Inbedrijfname")
    component_group     = OptionField('Component groep', options=['Generator', 'Motor', 'Electrical Equipment', 'Hulp', 'Transformer', 'Switch','Overig'], default='Overig')
    asset_description   = TextAreaField("Beschrijving")
    asset_photo_1       = FileField("Foto 1")
    asset_photo_2       = FileField("Foto 2")
    locatie             = GeoPointField('Locatie')
    
    upload_button       = ActionButton("Upload naar database", method='upload_entry')
    
    pass


class Controller(ViktorController):
    viktor_enforce_field_constraints = True  # Resolves upgrade instruction https://docs.viktor.ai/sdk/upgrades#U83

    label = 'My Entity Type'
    parametrization = Parametrization
    
    def upload_entry(self, params, **kwargs):
        data = [params.asset_name, params.asset_brand, params.serial_number, params.buy_year, params.on_year, params.component_group, params.asset_description]
        
        with open('assetdatabase.csv', 'a', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(data)
        file.close()

    @PlotlyView("Assets", duration_guess=15)
    def get_plotly_view(self, params, **kwargs):
        
        df = pd.read_csv('assetdatabase.csv')
        
        fig = go.Figure(
            data=[go.Table(
                header=dict(values=list(df.columns),
                fill_color='DarkOrange',
                align='left'),
                cells=dict(values=[df[column] for column in df.columns],
                fill_color='AliceBlue',
                align='left'))
            ])
        
        return PlotlyResult(fig.to_json())
    
    @MapView('Locatie Selectie', duration_guess=1)
    def get_map_view(self, params, **kwargs):
        marker = MapPoint(5.821153034001172, -55.16400368408251)
        features = [marker]
        return MapResult(features)
