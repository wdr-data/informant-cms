import json
import os
from enum import Enum
from functools import lru_cache
import logging

import dialogflow_v2 as dialogflow


AGENT = os.environ['DIALOGFLOW_AGENT']


class EntityType(Enum):
    GENRES = 'genres'
    TAGS = 'tags'


@lru_cache()
def get_entity_type_uuid(entity_type):
    entity_types_client = dialogflow.EntityTypesClient()
    parent = entity_types_client.project_agent_path(AGENT)
    entity_types = entity_types_client.list_entity_types(parent)
    for e in entity_types:
        if e.display_name == entity_type.value:
            uuid = e.name.split('/')[-1]
            return uuid


def add_entity(entity, entity_type):
    print(f'Adding Entity "{entity}" to {entity_type} in {AGENT}')
    uuid = get_entity_type_uuid(entity_type)

    entity_types_client = dialogflow.EntityTypesClient()
    parent = entity_types_client.entity_type_path(AGENT, uuid)

    new_entity = dialogflow.types.EntityType.Entity()
    new_entity.value = entity
    new_entity.synonyms.extend([entity])

    return entity_types_client.batch_create_entities(parent, [new_entity])


def delete_entity(entity, entity_type):
    print(f'Deleting Entity "{entity}" from {entity_type} in {AGENT}')
    uuid = get_entity_type_uuid(entity_type)

    entity_types_client = dialogflow.EntityTypesClient()
    parent = entity_types_client.entity_type_path(AGENT, uuid)

    return entity_types_client.batch_delete_entities(parent, [entity])


def update_entity_type(uuid, db_objects):
    entity_types_client = dialogflow.EntityTypesClient()
    parent = entity_types_client.entity_type_path(AGENT, uuid)

    existing_entities = [
        entity.value
        for entity in
        entity_types_client.get_entity_type(parent).entities
    ]

    new_entities = []

    for db_object in db_objects:
        if not db_object.name in existing_entities:
            new_entity = dialogflow.types.EntityType.Entity()
            new_entity.value = db_object.name
            new_entity.synonyms.extend([db_object.name])
            new_entities.append(new_entity)

    return entity_types_client.batch_create_entities(parent, new_entities)


def update_tags():
    from ..models.tag import ReportTag
    tags = ReportTag.objects.all()
    uuid = get_entity_type_uuid(EntityType.TAGS)
    return update_entity_type(uuid, tags)


def update_genres():
    from ..models.genre import Genre
    genres = Genre.objects.all()
    uuid = get_entity_type_uuid(EntityType.GENRES)
    return update_entity_type(uuid, genres)
