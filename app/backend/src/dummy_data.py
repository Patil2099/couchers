import json
import logging
from datetime import date

from couchers.crypto import hash_password
from couchers.db import get_user_by_field, session_scope
from couchers.models import (Base, Conversation, FriendRelationship,
                             FriendStatus, GroupChat, GroupChatRole,
                             GroupChatSubscription, Message, User)
from couchers.utils import Timestamp_from_datetime
from dateutil import parser
from sqlalchemy.exc import IntegrityError


def add_dummy_data(Session, file_name):
    try:
        logging.info(f"Adding dummy data")
        with session_scope(Session) as session:
            with open(file_name, "r") as file:
                data = json.loads(file.read())

            for user in data["users"]:
                new_user = User(
                    username=user["username"],
                    email=user["email"],
                    hashed_password=hash_password(user["password"]) if user["password"] else None,
                    name=user["name"],
                    city=user["city"],
                    verification=user["verification"],
                    community_standing=user["community_standing"],
                    birthdate=date(
                        year=user["birthdate"]["year"],
                        month=user["birthdate"]["month"],
                        day=user["birthdate"]["day"]
                    ),
                    gender=user["gender"],
                    languages="|".join(user["languages"]),
                    occupation=user["occupation"],
                    about_me=user["about_me"],
                    about_place=user["about_place"],
                    countries_visited="|".join(user["countries_visited"]),
                    countries_lived="|".join(user["countries_lived"]),
                )
                session.add(new_user)

            session.commit()

            for username1, username2 in data["friendships"]:
                friend_relationship = FriendRelationship(
                    from_user_id=get_user_by_field(session, username1).id,
                    to_user_id=get_user_by_field(session, username2).id,
                    status=FriendStatus.accepted,
                )
                session.add(friend_relationship)
            
            session.commit()

            for group_chat in data["group_chats"]:
                # Create the chat
                creator = group_chat["creator"]

                conversation = Conversation()
                session.add(conversation)

                chat = GroupChat(
                    conversation=conversation,
                    title=group_chat["title"],
                    creator_id=get_user_by_field(session, creator).id,
                    is_dm=group_chat["is_dm"],
                )
                session.add(chat)

                for participant in group_chat["participants"]:
                    subscription = GroupChatSubscription(
                        user_id=get_user_by_field(session, participant).id,
                        group_chat=chat,
                        role=GroupChatRole.admin if participant == creator else GroupChatRole.participant,
                    )
                    session.add(subscription)

                for message in group_chat["messages"]:
                    session.add(Message(
                        conversation=chat.conversation,
                        author_id=get_user_by_field(session, message["author"]).id,
                        time=parser.isoparse(message["time"]),
                        text=message["message"],
                    ))

            session.commit()


    except IntegrityError as e:
        logging.error("Failed to insert dummy data, is it already inserted?")