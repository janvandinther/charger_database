from viktor import ViktorController, File
from pathlib import Path
from PIL import Image
from viktor.parametrization import ViktorParametrization, TextField, IntegerField, TextAreaField, FileField, ActionButton, GeoPointField, OptionField, DateField
from viktor.views import PlotlyView, PlotlyResult, MapView, MapResult, MapPoint
import plotly.graph_objects as go
import csv
import pandas as pd
import shutil

entity_folder_path = Path(__file__).parent
file_path = entity_folder_path.parent / 'assetdatabase.csv'

class Parametrization(ViktorParametrization):
    asset_name          = TextField("Assetnaam")
    asset_brand         = TextField("Merk")
    serial_number       = IntegerField("Serienummer")
    buy_year            = DateField("Bouwjaar")
    on_year             = DateField("Inbedrijfname")
    component_group     = OptionField('Component group', options=['Generator', 'Motor', 'Common', 'Other'], default='Other')    
    common_group        = OptionField('Common group', options=['None', 'AC/DC', 'Air', 'Fire Fighting', 'Fuel', 'Lube Oil System', 'Monitoring and Control', 'Steam', 'Switchgear' , 'Waste Oil', 'Water Treatment and Cooling', 'Other'], default='None')
    location_name       = TextField("Locatienaam")
    location_coord      = GeoPointField('Locatie')
    asset_description   = TextAreaField("Beschrijving")
    asset_photo_1       = FileField("Foto 1")
    asset_photo_2       = FileField("Foto 2")
    
    
    upload_button       = ActionButton("Upload naar database", method='upload_entry')
    
    pass


class Controller(ViktorController):
    viktor_enforce_field_constraints = True  # Resolves upgrade instruction https://docs.viktor.ai/sdk/upgrades#U83

    label = 'My Entity Type'
    parametrization = Parametrization
    
    def upload_entry(self, params, **kwargs):
        data = [params.asset_name, params.asset_brand, params.serial_number, params.buy_year, params.on_year, params.component_group, params.common_group, params.asset_description, location_name, params.location_coord]
        
        with open(file_path, 'a', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(data)
        file.close()
            
    

    @PlotlyView("Assets", duration_guess=15)
    def get_plotly_view(self, params, **kwargs):
        
        df = pd.read_csv(file_path)
        
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
