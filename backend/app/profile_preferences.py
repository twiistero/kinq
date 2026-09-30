"""Versioned creation preferences. The existing public profile projection stays unchanged."""
import json
import re
from pathlib import Path
from typing import Literal
from pydantic import BaseModel, ConfigDict, Field, model_validator

_catalog_path = Path(__file__).resolve().parents[2] / 'content' / 'profile-kinks.json'
if not _catalog_path.exists():
    _catalog_path = Path('/srv/source/content/profile-kinks.json')
CATALOGUE = {item['id']: item for item in json.loads(_catalog_path.read_text())}


class KinkPreference(BaseModel):
    model_config = ConfigDict(extra='forbid')
    id: str = Field(max_length=80)
    interest: Literal['', 'interested', 'curious', 'favorite'] = ''
    role: str = Field(default='', max_length=40)
    experience: Literal['', 'new', 'some', 'regular'] = ''
    variants: list[str] = Field(default_factory=list, max_length=20)

    @model_validator(mode='after')
    def known_choices(self):
        item = CATALOGUE.get(self.id)
        if not item or self.role not in ['', *[role['id'] for role in item['roles']]]:
            raise ValueError('Univers ou rôle invalide')
        allowed = {variant['id'] for variant in item['variants']}
        if len(set(self.variants)) != len(self.variants) or not set(self.variants) <= allowed:
            raise ValueError('Nuances invalides')
        return self


class KinkPreferences(BaseModel):
    model_config = ConfigDict(extra='forbid')
    version: Literal[1]
    items: list[KinkPreference] = Field(default_factory=list, max_length=120)
    combinations: list[list[str]] = Field(default_factory=list, max_length=12)
    custom: str = Field(default='', max_length=300)

    @model_validator(mode='after')
    def coherent_combinations(self):
        ids = {item.id for item in self.items}
        if len(ids) != len(self.items):
            raise ValueError('Univers en double')
        seen = set()
        for mix in self.combinations:
            key = tuple(sorted(mix))
            if not 2 <= len(mix) <= 4 or len(set(mix)) != len(mix) or not set(mix) <= ids or key in seen:
                raise ValueError('Mélange invalide')
            seen.add(key)
        return self


class ProfileEdit(BaseModel):
    data: dict[str, str | bool | list[str] | KinkPreferences]

    @model_validator(mode='after')
    def coherent_profile(self):
        for key in ('style', 'practice'):
            values = self.data.get(key, [])
            if not isinstance(values, list) or len(values) > 120 or any(len(value) > 80 for value in values):
                raise ValueError('Univers invalides')
        for key, value in self.data.items():
            if len(key) > 80 or (key != 'kinkPreferences' and (isinstance(value, KinkPreferences) or len(str(value)) > (12000 if key in ('style', 'practice') else 2000))):
                raise ValueError('Champ invalide')
        preferences = self.data.get('kinkPreferences')
        if preferences is not None:
            if not isinstance(preferences, KinkPreferences):
                raise ValueError('Préférences invalides')
            for item in preferences.items:
                entry = CATALOGUE[item.id]
                # Legacy clients can send a style using its former classification.
                if entry['name'] not in self.data.get('style', []) + self.data.get('practice', []):
                    raise ValueError('Préférence associée à un univers non sélectionné')
        if len(json.dumps(self.model_dump(), ensure_ascii=False)) > 60000:
            raise ValueError('Profil trop long')
        age = str(self.data.get('age') or '')
        if age and (not re.fullmatch(r'[0-9]+', age) or not 18 <= int(age) <= 99):
            raise ValueError('Âge invalide')
        return self
