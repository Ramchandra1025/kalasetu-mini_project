
"use strict";

window.KalaSetuI18n = (() => {
  const STORAGE_KEY = "kalasetu_language";

  const languages = {
    en: "English",
    hi: "हिन्दी",
    kn: "ಕನ್ನಡ",
    mr: "मराठी"
  };

  const translations = {
    en: {
      "nav.workspace": "WORKSPACE",
      "nav.overview": "Overview",
      "nav.products": "My products",
      "nav.ai": "AI Studio",
      "nav.market": "Market intelligence",
      "nav.buyers": "Buyers & enquiries",
      "nav.orders": "Orders",
      "nav.inventory": "Inventory & production",
      "nav.sustainability": "Sustainability",
      "nav.analytics": "Business analytics",
      "nav.profile": "My craft profile",
      "nav.settings": "Settings & help",
      "dashboard.opportunity": "Your next opportunity",
      "dashboard.opportunityText":
        "Explore new ways to showcase your craft to the right buyers.",
      "dashboard.explore": "Explore opportunities",
      "settings.title": "Settings & help",
      "settings.subtitle":
        "Make your workspace more comfortable and accessible.",
      "settings.language": "Language preferences",
      "settings.accessibility": "Accessibility",
      "settings.help": "Help & support",
      "settings.languageLabel": "Website language",
      "settings.languageHelp":
        "Your language choice will be remembered on this browser.",
      "settings.save": "Save changes",
      "settings.accessibilitySave": "Save accessibility settings",
      "settings.largerText": "Larger text",
      "settings.largerTextHelp":
        "Increase text size for improved readability.",
      "settings.reduceMotion": "Reduce animations",
      "settings.reduceMotionHelp":
        "Limit motion and animated transitions.",
      "settings.helpProduct": "How do I add a product?",
      "settings.helpAI": "How can I use the AI tools?",
      "settings.helpLanguage": "How do I change my language?",
      "settings.helpProblem": "What if I find a problem?",
      "settings.profile": "My profile",
      "settings.artisanTitle": "Your craft. Your journey.",
      "settings.artisanText":
        "KalaSetu aims to help artisans present their craft and discover wider market opportunities.",
      "settings.tagline": "Rooted in tradition, open to opportunity.",
      "common.home": "Home",
      "common.save": "Save",
      "common.cancel": "Cancel",
      "common.loading": "Loading...",
      "common.error": "Something went wrong.",
      "common.retry": "Try again",
      "common.noPhoto": "No product photo",
      "common.saved": "Saved",
      "common.edit": "Edit",
      "common.details": "Details",
      "common.stock": "in stock",
      "common.emptyProducts":
        "Your catalogue is empty. Add your first product to get started.",
      "common.loadingProducts": "Loading your products...",
      "common.noEnquiries": "No enquiries yet",
      "common.productEnquiry": "Product enquiry",
      "common.buyer": "Buyer",
      "common.productNotSpecified": "Product not specified",
      "common.languageSaved":
        "Language preference saved in this browser.",
      "common.languageError":
        "Could not save the language preference."
    },

    hi: {
      "nav.workspace": "कार्यस्थल",
      "nav.overview": "अवलोकन",
      "nav.products": "मेरे उत्पाद",
      "nav.ai": "एआई स्टूडियो",
      "nav.market": "बाज़ार जानकारी",
      "nav.buyers": "खरीदार और पूछताछ",
      "nav.orders": "ऑर्डर",
      "nav.inventory": "स्टॉक और उत्पादन",
      "nav.sustainability": "स्थिरता",
      "nav.analytics": "व्यावसायिक विश्लेषण",
      "nav.profile": "मेरी शिल्प प्रोफ़ाइल",
      "nav.settings": "सेटिंग्स और सहायता",
      "dashboard.opportunity": "आपका अगला अवसर",
      "dashboard.opportunityText":
        "अपने शिल्प को सही खरीदारों तक पहुँचाने के नए तरीके खोजें।",
      "dashboard.explore": "अवसर देखें",
      "settings.title": "सेटिंग्स और सहायता",
      "settings.subtitle":
        "अपने कार्यक्षेत्र को अधिक सुविधाजनक और सुलभ बनाएं।",
      "settings.language": "भाषा की प्राथमिकताएं",
      "settings.accessibility": "सुलभता",
      "settings.help": "सहायता और समर्थन",
      "settings.languageLabel": "वेबसाइट की भाषा",
      "settings.languageHelp":
        "आपकी भाषा की पसंद इस ब्राउज़र में याद रखी जाएगी।",
      "settings.save": "बदलाव सहेजें",
      "settings.accessibilitySave": "सुलभता सेटिंग्स सहेजें",
      "settings.largerText": "बड़ा टेक्स्ट",
      "settings.largerTextHelp":
        "आसानी से पढ़ने के लिए टेक्स्ट का आकार बढ़ाएँ।",
      "settings.reduceMotion": "एनिमेशन कम करें",
      "settings.reduceMotionHelp":
        "गतिशील प्रभाव और एनिमेशन कम करें।",
      "settings.helpProduct": "मैं उत्पाद कैसे जोड़ूँ?",
      "settings.helpAI": "मैं एआई टूल्स का उपयोग कैसे करूँ?",
      "settings.helpLanguage": "मैं भाषा कैसे बदलूँ?",
      "settings.helpProblem": "समस्या मिलने पर क्या करें?",
      "settings.profile": "मेरी प्रोफ़ाइल",
      "settings.artisanTitle": "आपका शिल्प, आपकी यात्रा।",
      "settings.artisanText":
        "KalaSetu कारीगरों को अपना शिल्प प्रस्तुत करने और नए बाज़ार अवसर खोजने में मदद करता है।",
      "settings.tagline": "परंपरा से जुड़ा, नए अवसरों की ओर।",
      "common.home": "होम",
      "common.save": "सहेजें",
      "common.cancel": "रद्द करें",
      "common.loading": "लोड हो रहा है...",
      "common.error": "कुछ गलत हो गया।",
      "common.retry": "फिर कोशिश करें",
      "common.noPhoto": "उत्पाद की तस्वीर नहीं है",
      "common.saved": "सहेजा गया",
      "common.edit": "बदलें",
      "common.details": "विवरण",
      "common.stock": "स्टॉक में",
      "common.emptyProducts":
        "आपकी उत्पाद सूची खाली है। शुरू करने के लिए पहला उत्पाद जोड़ें।",
      "common.loadingProducts": "आपके उत्पाद लोड हो रहे हैं...",
      "common.noEnquiries": "अभी कोई पूछताछ नहीं है",
      "common.productEnquiry": "उत्पाद संबंधी पूछताछ",
      "common.buyer": "खरीदार",
      "common.productNotSpecified": "उत्पाद निर्दिष्ट नहीं है",
      "common.languageSaved":
        "भाषा की पसंद इस ब्राउज़र में सहेजी गई।",
      "common.languageError":
        "भाषा की पसंद सहेजी नहीं जा सकी।"
    },

    kn: {
      "nav.workspace": "ಕಾರ್ಯಸ್ಥಳ",
      "nav.overview": "ಅವಲೋಕನ",
      "nav.products": "ನನ್ನ ಉತ್ಪನ್ನಗಳು",
      "nav.ai": "AI ಸ್ಟುಡಿಯೋ",
      "nav.market": "ಮಾರುಕಟ್ಟೆ ಮಾಹಿತಿ",
      "nav.buyers": "ಖರೀದಿದಾರರು ಮತ್ತು ವಿಚಾರಣೆಗಳು",
      "nav.orders": "ಆರ್ಡರ್‌ಗಳು",
      "nav.inventory": "ದಾಸ್ತಾನು ಮತ್ತು ಉತ್ಪಾದನೆ",
      "nav.sustainability": "ಸುಸ್ಥಿರತೆ",
      "nav.analytics": "ವ್ಯವಹಾರ ವಿಶ್ಲೇಷಣೆ",
      "nav.profile": "ನನ್ನ ಕರಕುಶಲ ಪ್ರೊಫೈಲ್",
      "nav.settings": "ಸೆಟ್ಟಿಂಗ್‌ಗಳು ಮತ್ತು ಸಹಾಯ",
      "dashboard.opportunity": "ನಿಮ್ಮ ಮುಂದಿನ ಅವಕಾಶ",
      "dashboard.opportunityText":
        "ಸರಿಯಾದ ಖರೀದಿದಾರರಿಗೆ ನಿಮ್ಮ ಕರಕುಶಲವನ್ನು ತಲುಪಿಸುವ ಹೊಸ ಮಾರ್ಗಗಳನ್ನು ಅನ್ವೇಷಿಸಿ.",
      "dashboard.explore": "ಅವಕಾಶಗಳನ್ನು ಅನ್ವೇಷಿಸಿ",
      "settings.title": "ಸೆಟ್ಟಿಂಗ್‌ಗಳು ಮತ್ತು ಸಹಾಯ",
      "settings.subtitle":
        "ನಿಮ್ಮ ಕೆಲಸದ ಸ್ಥಳವನ್ನು ಹೆಚ್ಚು ಅನುಕೂಲಕರ ಮತ್ತು ಸುಲಭವಾಗಿ ಬಳಕೆಯಾಗುವಂತೆ ಮಾಡಿ.",
      "settings.language": "ಭಾಷೆಯ ಆದ್ಯತೆಗಳು",
      "settings.accessibility": "ಸುಲಭ ಬಳಕೆ",
      "settings.help": "ಸಹಾಯ ಮತ್ತು ಬೆಂಬಲ",
      "settings.languageLabel": "ವೆಬ್‌ಸೈಟ್ ಭಾಷೆ",
      "settings.languageHelp":
        "ನಿಮ್ಮ ಭಾಷೆಯ ಆಯ್ಕೆ ಈ ಬ್ರೌಸರ್‌ನಲ್ಲಿ ಉಳಿಯುತ್ತದೆ.",
      "settings.save": "ಬದಲಾವಣೆಗಳನ್ನು ಉಳಿಸಿ",
      "settings.accessibilitySave": "ಸುಲಭ ಬಳಕೆಯ ಸೆಟ್ಟಿಂಗ್‌ಗಳನ್ನು ಉಳಿಸಿ",
      "settings.largerText": "ದೊಡ್ಡ ಅಕ್ಷರಗಳು",
      "settings.largerTextHelp":
        "ಸುಲಭವಾಗಿ ಓದಲು ಅಕ್ಷರಗಳ ಗಾತ್ರವನ್ನು ಹೆಚ್ಚಿಸಿ.",
      "settings.reduceMotion": "ಅನಿಮೇಷನ್‌ಗಳನ್ನು ಕಡಿಮೆ ಮಾಡಿ",
      "settings.reduceMotionHelp":
        "ಚಲನೆ ಮತ್ತು ಅನಿಮೇಷನ್ ಪರಿಣಾಮಗಳನ್ನು ಕಡಿಮೆ ಮಾಡಿ.",
      "settings.helpProduct": "ಉತ್ಪನ್ನವನ್ನು ಹೇಗೆ ಸೇರಿಸುವುದು?",
      "settings.helpAI": "AI ಸಾಧನಗಳನ್ನು ಹೇಗೆ ಬಳಸುವುದು?",
      "settings.helpLanguage": "ಭಾಷೆಯನ್ನು ಹೇಗೆ ಬದಲಾಯಿಸುವುದು?",
      "settings.helpProblem": "ಸಮಸ್ಯೆ ಕಂಡುಬಂದರೆ ಏನು ಮಾಡಬೇಕು?",
      "settings.profile": "ನನ್ನ ಪ್ರೊಫೈಲ್",
      "settings.artisanTitle": "ನಿಮ್ಮ ಕಲೆ, ನಿಮ್ಮ ಪ್ರಯಾಣ.",
      "settings.artisanText":
        "ಕರಕುಶಲಕಾರರು ತಮ್ಮ ಕಲೆಯನ್ನು ಪರಿಚಯಿಸಿ ಹೊಸ ಮಾರುಕಟ್ಟೆ ಅವಕಾಶಗಳನ್ನು ಕಂಡುಕೊಳ್ಳಲು KalaSetu ಸಹಾಯ ಮಾಡುತ್ತದೆ.",
      "settings.tagline": "ಸಂಪ್ರದಾಯದ ಬೇರುಗಳು, ಹೊಸ ಅವಕಾಶಗಳತ್ತ.",
      "common.home": "ಮುಖಪುಟ",
      "common.save": "ಉಳಿಸಿ",
      "common.cancel": "ರದ್ದುಮಾಡಿ",
      "common.loading": "ಲೋಡ್ ಆಗುತ್ತಿದೆ...",
      "common.error": "ಏನೋ ತಪ್ಪಾಗಿದೆ.",
      "common.retry": "ಮತ್ತೆ ಪ್ರಯತ್ನಿಸಿ",
      "common.noPhoto": "ಉತ್ಪನ್ನದ ಚಿತ್ರವಿಲ್ಲ",
      "common.saved": "ಉಳಿಸಲಾಗಿದೆ",
      "common.edit": "ತಿದ್ದು",
      "common.details": "ವಿವರಗಳು",
      "common.stock": "ಸಂಗ್ರಹದಲ್ಲಿದೆ",
      "common.emptyProducts":
        "ನಿಮ್ಮ ಉತ್ಪನ್ನ ಪಟ್ಟಿ ಖಾಲಿಯಾಗಿದೆ. ಮೊದಲ ಉತ್ಪನ್ನವನ್ನು ಸೇರಿಸಿ.",
      "common.loadingProducts": "ನಿಮ್ಮ ಉತ್ಪನ್ನಗಳನ್ನು ಲೋಡ್ ಮಾಡಲಾಗುತ್ತಿದೆ...",
      "common.noEnquiries": "ಇನ್ನೂ ಯಾವುದೇ ವಿಚಾರಣೆಗಳಿಲ್ಲ",
      "common.productEnquiry": "ಉತ್ಪನ್ನ ವಿಚಾರಣೆ",
      "common.buyer": "ಖರೀದಿದಾರ",
      "common.productNotSpecified": "ಉತ್ಪನ್ನವನ್ನು ಸೂಚಿಸಲಾಗಿಲ್ಲ",
      "common.languageSaved":
        "ಭಾಷೆಯ ಆಯ್ಕೆಯನ್ನು ಈ ಬ್ರೌಸರ್‌ನಲ್ಲಿ ಉಳಿಸಲಾಗಿದೆ.",
      "common.languageError":
        "ಭಾಷೆಯ ಆಯ್ಕೆಯನ್ನು ಉಳಿಸಲಾಗಲಿಲ್ಲ."
    },

    mr: {
      "nav.workspace": "कार्यस्थळ",
      "nav.overview": "आढावा",
      "nav.products": "माझी उत्पादने",
      "nav.ai": "एआय स्टुडिओ",
      "nav.market": "बाजार माहिती",
      "nav.buyers": "खरेदीदार आणि चौकशी",
      "nav.orders": "ऑर्डर्स",
      "nav.inventory": "साठा आणि उत्पादन",
      "nav.sustainability": "शाश्वतता",
      "nav.analytics": "व्यवसाय विश्लेषण",
      "nav.profile": "माझे हस्तकला प्रोफाइल",
      "nav.settings": "सेटिंग्ज आणि मदत",
      "dashboard.opportunity": "तुमची पुढील संधी",
      "dashboard.opportunityText":
        "योग्य खरेदीदारांपर्यंत तुमची कला पोहोचवण्याचे नवीन मार्ग शोधा.",
      "dashboard.explore": "संधी शोधा",
      "settings.title": "सेटिंग्ज आणि मदत",
      "settings.subtitle":
        "तुमचे कार्यक्षेत्र अधिक सोयीचे आणि वापरण्यास सुलभ बनवा.",
      "settings.language": "भाषेची प्राधान्ये",
      "settings.accessibility": "सुलभता",
      "settings.help": "मदत आणि समर्थन",
      "settings.languageLabel": "वेबसाइटची भाषा",
      "settings.languageHelp":
        "तुमची भाषा निवड या ब्राउझरमध्ये जतन केली जाईल.",
      "settings.save": "बदल जतन करा",
      "settings.accessibilitySave": "सुलभता सेटिंग्ज जतन करा",
      "settings.largerText": "मोठा मजकूर",
      "settings.largerTextHelp":
        "वाचणे सोपे होण्यासाठी मजकूराचा आकार वाढवा.",
      "settings.reduceMotion": "ॲनिमेशन कमी करा",
      "settings.reduceMotionHelp":
        "हालचाल आणि ॲनिमेशनचे परिणाम कमी करा.",
      "settings.helpProduct": "उत्पादन कसे जोडायचे?",
      "settings.helpAI": "एआय साधने कशी वापरायची?",
      "settings.helpLanguage": "भाषा कशी बदलायची?",
      "settings.helpProblem": "समस्या आल्यास काय करावे?",
      "settings.profile": "माझे प्रोफाइल",
      "settings.artisanTitle": "तुमची कला, तुमचा प्रवास.",
      "settings.artisanText":
        "कारागिरांना त्यांची कला सादर करण्यासाठी आणि नवीन बाजारपेठेच्या संधी शोधण्यासाठी KalaSetu मदत करते.",
      "settings.tagline": "परंपरेशी नाते, नव्या संधींकडे वाटचाल.",
      "common.home": "मुख्यपृष्ठ",
      "common.save": "जतन करा",
      "common.cancel": "रद्द करा",
      "common.loading": "लोड होत आहे...",
      "common.error": "काहीतरी चूक झाली.",
      "common.retry": "पुन्हा प्रयत्न करा",
      "common.noPhoto": "उत्पादनाचा फोटो नाही",
      "common.saved": "जतन केले",
      "common.edit": "संपादित करा",
      "common.details": "तपशील",
      "common.stock": "साठ्यात",
      "common.emptyProducts":
        "तुमची उत्पादन यादी रिकामी आहे. सुरुवात करण्यासाठी पहिले उत्पादन जोडा.",
      "common.loadingProducts": "तुमची उत्पादने लोड होत आहेत...",
      "common.noEnquiries": "अद्याप कोणतीही चौकशी नाही",
      "common.productEnquiry": "उत्पादनाविषयी चौकशी",
      "common.buyer": "खरेदीदार",
      "common.productNotSpecified": "उत्पादन नमूद केलेले नाही",
      "common.languageSaved":
        "भाषेची निवड या ब्राउझरमध्ये जतन केली.",
      "common.languageError":
        "भाषेची निवड जतन करता आली नाही."
    }
  };

  let currentLanguage = "en";

  function get(key) {
    return translations[currentLanguage]?.[key]
      ?? translations.en[key]
      ?? key;
  }

  function apply(root = document) {
    root.querySelectorAll("[data-i18n]").forEach(element => {
      const key = element.dataset.i18n;

      // Translate only marked elements. Do not overwrite nested icons
      // or other HTML inside a container.
      if (key) element.textContent = get(key);
    });

    root.querySelectorAll("[data-i18n-placeholder]").forEach(element => {
      element.placeholder = get(element.dataset.i18nPlaceholder);
    });

    root.querySelectorAll("[data-i18n-title]").forEach(element => {
      element.title = get(element.dataset.i18nTitle);
    });

    root.querySelectorAll("[data-i18n-aria-label]").forEach(element => {
      element.setAttribute(
        "aria-label",
        get(element.dataset.i18nAriaLabel)
      );
    });

    if (root === document) {
      document.documentElement.lang = currentLanguage;
    }
  }

  function setLanguage(language) {
    if (!translations[language]) return false;

    currentLanguage = language;

    try {
      localStorage.setItem(STORAGE_KEY, language);
    } catch (error) {
      console.warn("Could not persist language preference.", error);
    }

    apply();

    document.dispatchEvent(new CustomEvent("kalasetu:languageChanged", {
      detail: { language }
    }));

    return true;
  }

  function init() {
    let savedLanguage = "en";

    try {
      savedLanguage = localStorage.getItem(STORAGE_KEY) || "en";
    } catch (error) {
      console.warn("Could not read saved language preference.", error);
    }

    currentLanguage = translations[savedLanguage]
      ? savedLanguage
      : "en";

    apply();
  }

  return {
    init,
    apply,
    get,
    setLanguage,
    getLanguage: () => currentLanguage,
    getLanguages: () => ({ ...languages })
  };
})();
