from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet
import requests
import json

class ActionSearchFlights(Action):

    def name(self) -> Text:
        return "action_search_flights"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        ville_depart = tracker.get_slot("ville_depart")
        ville_destination = tracker.get_slot("ville_destination")
        date_depart = tracker.get_slot("date_depart")
        date_retour = tracker.get_slot("date_retour")
        classe = tracker.get_slot("classe")
        type_vol = tracker.get_slot("type_vol")

        # Vérifier si des informations manquent
        missing_info = []
        if not ville_depart:
            missing_info.append("مدينة المغادرة")
        if not ville_destination:
            missing_info.append("مدينة الوصول")
        if not date_depart:
            missing_info.append("تاريخ المغادرة")

        if missing_info:
            message = f"""
            ℹ️ نحتاج بعض المعلومات الإضافية:
            {', '.join(missing_info)}
            
            مثال: "أريد السفر من الرباط إلى باريس يوم 15 يونيو"
            """
            dispatcher.utter_message(text=message)
            return []

        # Simulation d'appel API avec prix variable
        prices = {
            "اقتصادية": "1200 درهم",
            "درجة أولى": "4500 درهم",
            "درجة الأعمال": "2800 درهم"
        }
        
        flight_info = {
            "from": ville_depart,
            "to": ville_destination,
            "departure": date_depart,
            "return": date_retour if type_vol == "ذهاب وإياب" else None,
            "class": classe or "اقتصادية",
            "price": prices.get(classe or "اقتصادية", "1200 درهم")
        }

        message = f"""
        🛫 وجدت لك رحلة ممتازة:
        
        ✈️ من: {flight_info['from']}
        📍 إلى: {flight_info['to']}
        📅 تاريخ المغادرة: {flight_info['departure']}
        {'📅 تاريخ العودة: ' + flight_info['return'] if flight_info['return'] else ''}
        💺 الدرجة: {flight_info['class']}
        💰 السعر: {flight_info['price']}
        
        هل توافق على هذا الاختيار؟ أم تريد تغيير شيء؟
        """

        dispatcher.utter_message(text=message)
        return []

class ActionResetSlots(Action):

    def name(self) -> Text:
        return "action_reset_slots"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        # Réinitialiser tous les slots
        return [
            SlotSet("ville_depart", None),
            SlotSet("ville_destination", None),
            SlotSet("date_depart", None),
            SlotSet("date_retour", None),
            SlotSet("classe", None),
            SlotSet("type_vol", None),
            SlotSet("ville_hotel", None),
            SlotSet("categorie_hotel", None),
            SlotSet("quartier", None),
            SlotSet("nombre_personnes", None)
        ]

class ActionSearchHotels(Action):

    def name(self) -> Text:
        return "action_search_hotels"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        ville_hotel = tracker.get_slot("ville_hotel")
        categorie_hotel = tracker.get_slot("categorie_hotel")
        quartier = tracker.get_slot("quartier")
        nombre_personnes = tracker.get_slot("nombre_personnes")

        # Vérifier si des informations manquent
        missing_info = []
        if not ville_hotel:
            missing_info.append("المدينة")
        if not categorie_hotel:
            missing_info.append("تصنيف الفندق")

        if missing_info:
            message = f"""
            ℹ️ نحتاج بعض المعلومات الإضافية:
            {', '.join(missing_info)}
            
            مثال: "فندق 4 نجوم في مراكش"
            """
            dispatcher.utter_message(text=message)
            return []

        # Simulation d'appel API avec prix variable selon la catégorie
        hotel_names = {
            "5 نجوم": "فندق الأطلس الذهبي",
            "4 نجوم": "فندق المغرب الجميل", 
            "3 نجوم": "فندق الضيافة"
        }
        
        prices = {
            "5 نجوم": "1200 درهم/ليلة",
            "4 نجوم": "800 درهم/ليلة",
            "3 نجوم": "400 درهم/ليلة"
        }

        hotel_info = {
            "name": hotel_names.get(categorie_hotel, "فندق الضيافة"),
            "city": ville_hotel,
            "category": categorie_hotel,
            "district": quartier or "وسط المدينة",
            "guests": nombre_personnes or "2",
            "price": prices.get(categorie_hotel, "600 درهم/ليلة")
        }

        message = f"""
        🏨 وجدت لك فندق رائع:
        
        🏛️ اسم الفندق: {hotel_info['name']}
        📍 المدينة: {hotel_info['city']}
        ⭐ التصنيف: {hotel_info['category']}
        🗺️ المنطقة: {hotel_info['district']}
        👥 عدد الأشخاص: {hotel_info['guests']}
        💰 السعر: {hotel_info['price']}
        
        هل توافق على هذا الاختيار؟ أم تريد تغيير شيء؟
        """

        dispatcher.utter_message(text=message)
        return []

class ActionConfirmBooking(Action):

    def name(self) -> Text:
        return "action_confirm_booking"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        booking_ref = "TRV" + str(hash(tracker.sender_id))[-6:]
        
        message = f"""
        ✅ تم تأكيد حجزك بنجاح!
        
        📋 رقم المرجع: {booking_ref}
        
        🙏 شكراً لثقتك بوكالة السفر لدينا!
        نتطلع إلى خدمتك مرة أخرى.
        
        رحلة سعيدة! ✈️🌟
        
        وداعاً وإلى اللقاء! 👋
        """

        dispatcher.utter_message(text=message)
        return []

class ActionChangeOptions(Action):

    def name(self) -> Text:
        return "action_change_options"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        # Récupérer les slots actuels pour affichage
        current_slots = {
            "ville_depart": tracker.get_slot("ville_depart"),
            "ville_destination": tracker.get_slot("ville_destination"),
            "date_depart": tracker.get_slot("date_depart"),
            "date_retour": tracker.get_slot("date_retour"),
            "classe": tracker.get_slot("classe"),
            "type_vol": tracker.get_slot("type_vol"),
            "ville_hotel": tracker.get_slot("ville_hotel"),
            "categorie_hotel": tracker.get_slot("categorie_hotel"),
            "quartier": tracker.get_slot("quartier"),
            "nombre_personnes": tracker.get_slot("nombre_personnes")
        }

        # Créer un message avec les valeurs actuelles
        current_info = []
        if current_slots["ville_depart"]:
            current_info.append(f"مدينة المغادرة: {current_slots['ville_depart']}")
        if current_slots["ville_destination"]:
            current_info.append(f"مدينة الوصول: {current_slots['ville_destination']}")
        if current_slots["date_depart"]:
            current_info.append(f"تاريخ المغادرة: {current_slots['date_depart']}")
        if current_slots["date_retour"]:
            current_info.append(f"تاريخ العودة: {current_slots['date_retour']}")
        if current_slots["ville_hotel"]:
            current_info.append(f"مدينة الفندق: {current_slots['ville_hotel']}")
        if current_slots["categorie_hotel"]:
            current_info.append(f"تصنيف الفندق: {current_slots['categorie_hotel']}")

        current_display = "\n".join(current_info) if current_info else "لا توجد معلومات محفوظة"

        message = f"""
        🔄 حسناً! يمكنك تعديل اختيارك.
        
        📋 المعلومات الحالية:
        {current_display}
        
        💡 يمكنك تغيير أي من هذه المعلومات بقول:
        • "أريد السفر من الرباط إلى دبي"
        • "تغيير التاريخ إلى 20 يونيو"
        • "فندق في مراكش بدلاً من ذلك"
        • "3 أشخاص بدلاً من 2"
        
        أخبرني بالتغيير الذي تريده! 🔍
        """

        dispatcher.utter_message(text=message)
        return []