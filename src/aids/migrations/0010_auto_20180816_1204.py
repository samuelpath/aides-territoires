# Generated by Django 2.1 on 2018-08-16 10:04

from django.db import migrations
import geofr.fields


class Migration(migrations.Migration):

    dependencies = [
        ('aids', '0009_auto_20180816_1203'),
    ]

    operations = [
        migrations.AddField(
            model_name='aid',
            name='application_department',
            field=geofr.fields.DepartmentField(blank=True, choices=[('01', 'Ain'), ('02', 'Aisne'), ('84', '03'), ('04', 'Alpes-de-Haute-Provence'), ('93', '05'), ('06', 'Alpes-Maritimes'), ('84', '07'), ('08', 'Ardennes'), ('76', '09'), ('10', 'Aube'), ('76', '11'), ('12', 'Aveyron'), ('93', '13'), ('14', 'Calvados'), ('84', '15'), ('16', 'Charente'), ('75', '17'), ('18', 'Cher'), ('75', '19'), ('21', "Côte-d'Or"), ('53', '22'), ('23', 'Creuse'), ('75', '24'), ('25', 'Doubs'), ('84', '26'), ('27', 'Eure'), ('24', '28'), ('29', 'Finistère'), ('94', '2A'), ('2B', 'Haute-Corse'), ('76', '30'), ('31', 'Haute-Garonne'), ('76', '32'), ('33', 'Gironde'), ('76', '34'), ('35', 'Ille-et-Vilaine'), ('24', '36'), ('37', 'Indre-et-Loire'), ('84', '38'), ('39', 'Jura'), ('75', '40'), ('41', 'Loir-et-Cher'), ('84', '42'), ('43', 'Haute-Loire'), ('52', '44'), ('45', 'Loiret'), ('76', '46'), ('47', 'Lot-et-Garonne'), ('76', '48'), ('49', 'Maine-et-Loire'), ('28', '50'), ('51', 'Marne'), ('44', '52'), ('53', 'Mayenne'), ('44', '54'), ('55', 'Meuse'), ('53', '56'), ('57', 'Moselle'), ('27', '58'), ('59', 'Nord'), ('32', '60'), ('61', 'Orne'), ('32', '62'), ('63', 'Puy-de-Dôme'), ('75', '64'), ('65', 'Hautes-Pyrénées'), ('76', '66'), ('67', 'Bas-Rhin'), ('44', '68'), ('69', 'Rhône'), ('27', '70'), ('71', 'Saône-et-Loire'), ('52', '72'), ('73', 'Savoie'), ('84', '74'), ('75', 'Paris'), ('28', '76'), ('77', 'Seine-et-Marne'), ('11', '78'), ('79', 'Deux-Sèvres'), ('32', '80'), ('81', 'Tarn'), ('76', '82'), ('83', 'Var'), ('93', '84'), ('85', 'Vendée'), ('75', '86'), ('87', 'Haute-Vienne'), ('44', '88'), ('89', 'Yonne'), ('27', '90'), ('91', 'Essonne'), ('11', '92'), ('93', 'Seine-Saint-Denis'), ('11', '94'), ('95', "Val-d'Oise"), ('971', 'Guadeloupe'), ('972', 'Martinique'), ('973', 'Guyane'), ('974', 'La Réunion'), ('976', 'Mayotte')], max_length=3, null=True, verbose_name='Application department'),
        ),
        migrations.AddField(
            model_name='aid',
            name='application_region',
            field=geofr.fields.RegionField(blank=True, choices=[('01', 'Guadeloupe'), ('02', 'Martinique'), ('03', 'Guyane'), ('04', 'La Réunion'), ('06', 'Mayotte'), ('11', 'Île-de-France'), ('24', 'Centre-Val de Loire'), ('27', 'Bourgogne-Franche-Comté'), ('28', 'Normandie'), ('32', 'Hauts-de-France'), ('44', 'Grand Est'), ('52', 'Pays de la Loire'), ('53', 'Bretagne'), ('75', 'Nouvelle-Aquitaine'), ('76', 'Occitanie'), ('84', 'Auvergne-Rhône-Alpes'), ('93', "Provence-Alpes-Côte d'Azur"), ('94', 'Corse')], max_length=2, null=True, verbose_name='Application region'),
        ),
    ]
