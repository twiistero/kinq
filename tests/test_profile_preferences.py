import unittest
from pydantic import ValidationError
from backend.app.profile_preferences import CATALOGUE, ProfileEdit


def payload():
    return {'style':['Leather'], 'practice':['Bondage'], 'age':'32', 'kinkPreferences':{'version':1, 'items':[{'id':'leather','role':'wear','variants':['harnais']},{'id':'bondage','role':'tied'}], 'combinations':[['leather','bondage']]}}


class ProfilePreferencesTests(unittest.TestCase):
    def test_round_trip_and_legacy(self):
        data = ProfileEdit(data=payload()).model_dump()
        self.assertEqual(ProfileEdit(**data).model_dump(), data)
        self.assertEqual(ProfileEdit(data={'practice':['Bondage'], 'bondageDetail':'Être attaché'}).data['bondageDetail'], 'Être attaché')

    def test_every_catalogue_choice_and_large_profile(self):
        data = {'style':[], 'practice':[], 'kinkPreferences':{'version':1,'items':[]}}
        for key, item in CATALOGUE.items():
            data[item['field']].append(item['name'])
            for role in item['roles']:
                ProfileEdit(data={item['field']:[item['name']], 'kinkPreferences':{'version':1,'items':[{'id':key,'role':role['id'],'variants':[v['id'] for v in item['variants']]}]}})
            data['kinkPreferences']['items'].append({'id':key,'role':item['roles'][0]['id'],'variants':[v['id'] for v in item['variants']]})
            self.assertTrue(set(item['related']) <= set(CATALOGUE))
        self.assertEqual(len(ProfileEdit(data=data).data['kinkPreferences'].items), len(CATALOGUE))

    def test_invalid_roles_variants_and_unselected_kinks(self):
        for update in [{'role':'dom'}, {'variants':['invented']}, {'id':'missing'}]:
            data=payload();data['kinkPreferences']['items'][0].update(update)
            with self.subTest(update=update), self.assertRaises(ValidationError): ProfileEdit(data=data)
        data=payload();data['style']=[]
        with self.assertRaises(ValidationError): ProfileEdit(data=data)

    def test_invalid_mixes(self):
        for mixes in [[['leather']], [['leather','leather']], [['leather','unknown']], [['leather','bondage'],['bondage','leather']]]:
            data=payload();data['kinkPreferences']['combinations']=mixes
            with self.subTest(mixes=mixes), self.assertRaises(ValidationError): ProfileEdit(data=data)

    def test_bounds_and_types(self):
        for key,value in [('age','17'),('age','100'),('age',True),('style','Leather'),('kinkPreferences','bad')]:
            data=payload();data[key]=value
            with self.subTest(key=key,value=value), self.assertRaises(ValidationError): ProfileEdit(data=data)
        data=payload();data['kinkPreferences']['custom']='x'*301
        with self.assertRaises(ValidationError): ProfileEdit(data=data)


if __name__ == '__main__': unittest.main()
