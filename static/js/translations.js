const translations = {
    "en": {
        "title": "Agri-Vision",
        "subtitle": "Enter your soil and environmental details to get intelligent crop recommendations.",
        "tab_crop": "🌱 Crop Intelligence",
        "tab_fert": "🧪 Fertilizer Calculator",
        "map_label": "Select Location on Map 📍",
        "map_hint": "Clicking the map will automatically fill your City, State, District, and Rainfall below.",
        "nitrogen": "Nitrogen (N)",
        "phosphorous": "Phosphorous (P)",
        "potassium": "Potassium (K)",
        "ph": "Soil pH",
        "state": "State",
        "district": "District",
        "select_state": "Select state",
        "select_district": "Select district",
        "rainfall": "Rainfall (mm)",
        "rainfall_hint": "(Auto-filled by district)",
        "city": "City / Town (For Weather)",
        "generate": "Generate Farm Insights ✨",
        "report_title": "Intelligence Report",
        "top_crop": "Top Recommended Crop",
        "profit": "Expected Profit",
        "yield": "Estimated Yield",
        "cost": "Total Cost",
        "financial_risk": "⚖️ Financial Risk Assessment",
        "best_case": "🚀 Best Case Scenario",
        "worst_case": "📉 Worst Case Scenario",
        "monthly_revenue": "📈 Monthly Revenue Forecast (2026)",
        "cost_breakdown": "📊 Cost Breakdown (Estimated)",
        "seed": "Seed",
        "fertilizer": "Fertilizer",
        "manure": "Manure",
        "labor": "Labor",
        "machine": "Machine",
        "soil_env": "🌍 Soil & Environment Snapshot",
        "ai_reasoning": "🤖 AI Recommendation Reasoning",
        "download_pdf": "Download PDF",
        "compare_alt": "Compare Alternatives",
        "forecast": "🌤️ 5-Day Weather Forecast",
        "return_dash": "Return to Dashboard",
        "smart_insights": "🧠 Smart Insights",
        "govt_schemes": "🏛️ Government Schemes For You",
        "schemes_desc": "Personalized recommendations based on your crop, state, and soil conditions.",
        "crop_schemes": "Crop-Specific Schemes",
        "state_schemes": "State Schemes",
        "condition_schemes": "Recommended For Your Conditions",
        "central_schemes": "Central Government Schemes"
    },
    "hi": {
        "title": "एग्री-विजन (Agri-Vision)",
        "subtitle": "बुद्धिमान फसल सिफारिशें प्राप्त करने के लिए अपनी मिट्टी और पर्यावरण विवरण दर्ज करें।",
        "tab_crop": "🌱 फसल बुद्धिमत्ता",
        "tab_fert": "🧪 उर्वरक कैलकुलेटर",
        "map_label": "नक्शे पर स्थान चुनें 📍",
        "map_hint": "नक्शे पर क्लिक करने से आपका शहर, राज्य, जिला और वर्षा अपने आप भर जाएगी।",
        "nitrogen": "नाइट्रोजन (N)",
        "phosphorous": "फास्फोरस (P)",
        "potassium": "पोटैशियम (K)",
        "ph": "मिट्टी का पीएच (pH)",
        "state": "राज्य",
        "district": "जिला",
        "select_state": "राज्य चुनें",
        "select_district": "जिला चुनें",
        "rainfall": "वर्षा (मिमी)",
        "rainfall_hint": "(जिले द्वारा स्वतः भरा गया)",
        "city": "शहर / कस्बा (मौसम के लिए)",
        "generate": "खेत की जानकारी प्राप्त करें ✨",
        "report_title": "खुफिया रिपोर्ट",
        "top_crop": "शीर्ष अनुशंसित फसल",
        "profit": "अपेक्षित लाभ",
        "yield": "अनुमानित उपज",
        "cost": "कुल लागत",
        "financial_risk": "⚖️ वित्तीय जोखिम मूल्यांकन",
        "best_case": "🚀 सर्वश्रेष्ठ परिदृश्य",
        "worst_case": "📉 सबसे खराब परिदृश्य",
        "monthly_revenue": "📈 मासिक राजस्व पूर्वानुमान (2026)",
        "cost_breakdown": "📊 लागत विवरण (अनुमानित)",
        "seed": "बीज",
        "fertilizer": "उर्वरक",
        "manure": "खाद",
        "labor": "मजदूरी",
        "machine": "मशीन",
        "soil_env": "🌍 मिट्टी और पर्यावरण स्नैपशॉट",
        "ai_reasoning": "🤖 एआई सिफारिश तर्क",
        "download_pdf": "पीडीएफ डाउनलोड करें",
        "compare_alt": "विकल्पों की तुलना करें",
        "forecast": "🌤️ 5-दिवसीय मौसम पूर्वानुमान",
        "return_dash": "डैशबोर्ड पर लौटें",
        "smart_insights": "🧠 स्मार्ट इनसाइट्स",
        "govt_schemes": "🏛️ आपके लिए सरकारी योजनाएं",
        "schemes_desc": "आपकी फसल, राज्य और मिट्टी की स्थिति के आधार पर व्यक्तिगत सिफारिशें।",
        "crop_schemes": "फसल-विशिष्ट योजनाएं",
        "state_schemes": "राज्य योजनाएं",
        "condition_schemes": "आपकी स्थितियों के लिए अनुशंसित",
        "central_schemes": "केंद्र सरकार की योजनाएं"
    }
};

const cropTranslations = {
    "rice": "चावल (Rice)",
    "maize": "मक्का (Maize)",
    "jute": "जूट (Jute)",
    "cotton": "कपास (Cotton)",
    "coconut": "नारियल (Coconut)",
    "papaya": "पपीता (Papaya)",
    "orange": "संतरा (Orange)",
    "apple": "सेब (Apple)",
    "muskmelon": "खरबूजा (Muskmelon)",
    "watermelon": "तरबूज (Watermelon)",
    "grapes": "अंगूर (Grapes)",
    "mango": "आम (Mango)",
    "banana": "केला (Banana)",
    "pomegranate": "अनार (Pomegranate)",
    "lentil": "मसूर (Lentil)",
    "blackgram": "उड़द (Blackgram)",
    "mungbean": "मूंग (Mungbean)",
    "mothbeans": "मोठ (Mothbeans)",
    "pigeonpeas": "अरहर (Pigeonpeas)",
    "kidneybeans": "राजमा (Kidneybeans)",
    "chickpea": "चना (Chickpea)",
    "coffee": "कॉफी (Coffee)",
    "wheat": "गेहूं (Wheat)",
    "sugarcane": "गन्ना (Sugarcane)",
    "tea": "चाय (Tea)",
    "mustard": "सरसों (Mustard)",
    "soyabean": "सोयाबीन (Soyabean)",
    "barley": "जौ (Barley)",
    "groundnut": "मूंगफली (Groundnut)",
    "bajra": "बाजरा (Bajra)",
    "jowar": "ज्वार (Jowar)",
    "ragi": "रागी (Ragi)"
};

function translatePage() {
    const currentLang = localStorage.getItem('language') || 'en';
    document.querySelectorAll('[data-i18n]').forEach(el => {
        const key = el.getAttribute('data-i18n');
        if (translations[currentLang] && translations[currentLang][key]) {
            // Keep the innerHTML tags if they exist, but replace text.
            // A simple way is to replace the textContent, but some have spans inside.
            // For safety, we just set innerHTML.
            if(key === 'rainfall') {
                el.innerHTML = translations[currentLang][key] + ' <span style="font-size: 0.8rem; color: var(--text-light); font-weight: normal;" data-i18n="rainfall_hint">' + translations[currentLang]["rainfall_hint"] + '</span>';
            } else {
                el.innerText = translations[currentLang][key];
            }
        }
    });

    // Translate dynamic crop names if any
    document.querySelectorAll('.dynamic-crop').forEach(el => {
        let text = el.getAttribute('data-original-crop') || el.innerText.toLowerCase();
        if (!el.getAttribute('data-original-crop')) {
            el.setAttribute('data-original-crop', text);
        }
        
        // Remove spaces and make lowercase for lookup
        let lookupText = text.trim().toLowerCase();
        if (currentLang === 'hi' && cropTranslations[lookupText]) {
            el.innerText = cropTranslations[lookupText];
        } else {
            // fallback to Title Case English
            el.innerText = lookupText.charAt(0).toUpperCase() + lookupText.slice(1);
        }
    });
    
    // Update active state of language buttons if they exist
    const btnEn = document.getElementById('lang-en');
    const btnHi = document.getElementById('lang-hi');
    if (btnEn && btnHi) {
        if (currentLang === 'en') {
            btnEn.style.fontWeight = 'bold';
            btnHi.style.fontWeight = 'normal';
        } else {
            btnEn.style.fontWeight = 'normal';
            btnHi.style.fontWeight = 'bold';
        }
    }
}

function setLanguage(lang) {
    localStorage.setItem('language', lang);
    translatePage();
}

// Run on load
document.addEventListener('DOMContentLoaded', translatePage);
