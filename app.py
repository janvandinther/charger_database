from viktor import ViktorController, File
from pathlib import Path
from PIL import Image
from viktor.parametrization import ViktorParametrization, TextField, IntegerField, TextAreaField, FileField, ActionButton, GeoPointField, OptionField, DateField, Page, Section, LineBreak, DownloadButton
from viktor.views import PlotlyView, PlotlyResult, MapView, MapResult, MapPoint
from viktor.result import DownloadResult
import plotly.graph_objects as go
import csv
import pandas as pd
import shutil

entity_folder_path = Path(__file__)
file_path = entity_folder_path.parent / 'assetdatabase.csv'

class Parametrization(ViktorParametrization):
    page_input =    Page("Voeg toe & Pas aan", views = ['asset_view','location_view'])
    page_results =  Page("Overzicht Assets", views = ['assets_map_view'])
    
    page_input.section_input = Section("Voeg asset toe")
    page_input.section_change = Section("Pas asset aan")
    
    page_input.section_input.asset_name          = TextField("Assetnaam")
    page_input.section_input.asset_brand         = TextField("Merk")
    page_input.section_input.serial_number       = IntegerField("Serienummer")
    page_input.section_input.buy_year            = IntegerField("Bouwjaar")
    page_input.section_input.on_year             = IntegerField("Inbedrijfname")
    page_input.section_input.component_group     = OptionField('Component groep', options=['Generator', 'Motor', 'Common', 'Other'], default='Other')    
    page_input.section_input.common_group        = OptionField('Common groep', options=['None', 'AC/DC', 'Air', 'Fire Fighting', 'Fuel', 'Lube Oil System', 'Monitoring and Control', 'Steam', 'Switchgear' , 'Waste Oil', 'Water Treatment and Cooling', 'Other'], default='None')
    page_input.section_input.location_name       = TextField("Locatienaam")
    page_input.section_input.location_coord      = GeoPointField('Locatie')
    page_input.section_input.asset_description   = TextAreaField("Beschrijving")
    page_input.section_input.asset_photo_1       = FileField("Foto 1")
    page_input.section_input.asset_photo_2       = FileField("Foto 2")
    page_input.section_input.upload_button       = ActionButton("Upload naar database", method='upload_entry')
    
    page_input.section_change.select_serialnumber   = IntegerField('Serienummer')
    page_input.section_change.lb1                   = LineBreak()
    page_input.section_change.select_attribute      = OptionField('Eigenschap', options = ['Assetnaam', 'Merk', 'Serienummer','Bouwjaar','Inbedrijfname','Component groep','Common groep', 'Locatienaam','Locatie','Beschrijving'])
    page_input.section_change.new_value             = TextField("Nieuwe waarde")
    page_input.section_change.new_location           = GeoPointField('Nieuwe locatie')
    page_input.section_change.change_button         = ActionButton("Pas aan", method='change_entry')
    page_input.section_change.delete_button         = ActionButton("Verwijder uit database", method='delete_entry')
    
    page_results.download_button       = DownloadButton("Download", method='download_file')
    
    pass


class Controller(ViktorController):
    viktor_enforce_field_constraints = True  # Resolves upgrade instruction https://docs.viktor.ai/sdk/upgrades#U83

    label = 'ESB Asset Inventarisator'
    parametrization = Parametrization
    
    def upload_entry(self, params, **kwargs):
        data = [
            params.page_input.section_input.asset_name, 
            params.page_input.section_input.asset_brand, 
            params.page_input.section_input.serial_number, 
            params.page_input.section_input.buy_year, 
            params.page_input.section_input.on_year, 
            params.page_input.section_input.component_group, 
            params.page_input.section_input.common_group, 
            params.page_input.section_input.asset_description, 
            params.page_input.section_input.location_name, 
            params.page_input.section_input.location_coord
            ]
        
        df = pd.read_csv(file_path)
        df.loc[len(df)] = data
        df.to_csv(file_path, index=False)
        print(df.columns)
        
    
    def change_entry(self, params, **kwargs):
        if params.page_input.section_change.select_attribute in ["Assetnaam", "Merk", "Component groep", "Common groep","Beschrijving"]:
            df = pd.read_csv(file_path)
            print(df.columns)
            index = df.loc[df['Serienummer'] == params.page_input.section_change.select_serialnumber].index[0]
            df.at[index, params.page_input.section_change.select_attribute] = params.page_input.section_change.new_value
            df.to_csv(file_path, index=False)
        else:
            if params.page_input.section_change.select_attribute != "Locatie":
                df = pd.read_csv(file_path)
                index = df.loc[df['Serienummer'] == params.page_input.section_change.select_serialnumber].index[0]
                df.at[index, params.page_input.section_change.select_attribute] = int(params.page_input.section_change.new_value)
                df.to_csv(file_path, index=False)
            else:
                df = pd.read_csv(file_path)
                index = df.loc[df['Serienummer'] == params.page_input.section_change.select_serialnumber].index[0]
                df.at[index, params.page_input.section_change.select_attribute] = params.page_input.section_change.new_location
                df.to_csv(file_path, index=False)
                
    def delete_entry(self,params, **kwargs):
        df = pd.read_csv(file_path)
        index = df.loc[df['Serienummer'] == params.page_input.section_change.select_serialnumber].index[0]
        df.drop(index, inplace=True)
        df.to_csv(file_path, index=False)
        
    def download_file(self, params, **kwargs):
       
        file = File.from_path(file_path)
        return DownloadResult(file, 'asset_database_EBS.csv')
            
    

    @PlotlyView("Assets", duration_guess=15)
    def asset_view(self, params, **kwargs):
        
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
    def location_view(self, params, **kwargs):
        marker = MapPoint(5.905264411741596, -57.02917512726031)
        features = [marker]
        return MapResult(features)
    
    @MapView('Assets op kaart', duration_guess=1)
    def assets_map_view(self, params, **kwargs):
        marker = MapPoint(5.905264411741596, -57.02917512726031)
        features = [marker]
        return MapResult(features)

