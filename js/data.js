const GITA_DATA = {
  adhyays: [
    {
      id: 1, number: "१", name: "अर्जुनविषादयोग", emoji: "😔",
      available: false, concepts: []
    },
    {
      id: 2, number: "२", name: "सांख्ययोग", emoji: "🧘",
      available: false, concepts: []
    },
    {
      id: 3, number: "३", name: "कर्मयोग", emoji: "🌾",
      available: true,
      summary: "कर्मयोग हे गीतेतील सर्वात व्यावहारिक तत्त्वज्ञान आहे. माणूस एक क्षणही कर्माशिवाय राहू शकत नाही — प्रश्न फक्त ते कोणत्या भावनेने करायचे. यज्ञभावाने कर्म करणे, ईश्वराला अर्पण करणे, लोकसंग्रहाची जबाबदारी सांभाळणे — हाच कर्मयोग. राग-द्वेष, काम-क्रोध हे अदृश्य शत्रू आहेत. ज्ञान नाहीसे होत नाही — ते झाकले जाते. साधना म्हणजे पडदा हटवणे.",
      concepts: [
        { id: 1,  emoji: "⚖️", name: "सांख्य विरुद्ध कर्मयोग" },
        { id: 2,  emoji: "⚙️", name: "कर्म अनिवार्य आहे" },
        { id: 3,  emoji: "🔥", name: "यज्ञ — परस्पर-पोषण" },
        { id: 4,  emoji: "🌧️", name: "यज्ञ-पर्जन्य-अन्न — विश्वचक्र" },
        { id: 5,  emoji: "🌟", name: "लोकसंग्रह" },
        { id: 6,  emoji: "🌊", name: "आसक्त विरुद्ध अनासक्त कर्मी" },
        { id: 7,  emoji: "🙏", name: "ईश्वरार्पण" },
        { id: 8,  emoji: "🌱", name: "स्वधर्म विरुद्ध परधर्म" },
        { id: 9,  emoji: "👁️", name: "राग-द्वेष — लपलेले शत्रू" },
        { id: 10, emoji: "⚔️", name: "काम-क्रोध — महाशत्रू" },
        { id: 11, emoji: "🐎", name: "इंद्रिय निग्रह — श्रेष्ठता क्रम" },
        { id: 12, emoji: "💡", name: "ज्ञान झाकणारा काम" }
      ]
    },
    {
      id: 4, number: "४", name: "ज्ञानयोग", emoji: "✨",
      available: true,
      summary: "ज्ञानयोग हे गीतेचे हृदय आहे. कृष्ण अवताराचे रहस्य उलगडतो, कर्म-अकर्म-विकर्माचा विवेक सांगतो, यज्ञाचे अनेक प्रकार दाखवतो आणि ज्ञानाग्नीची अपार शक्ती विशद करतो. \"श्रद्धावान् लभते ज्ञानम्\" — श्रद्धा असेल तर ज्ञान मिळतेच. हा अध्याय आपल्याला शिकवतो — ज्ञान हे केवळ पुस्तकी नाही, ते जीवन जगण्याची कला आहे.",
      concepts: [
        { id: 1,  emoji: "🌅", name: "अवताराचं रहस्य" },
        { id: 2,  emoji: "⚡", name: "ईश्वराचं निर्लिप्त कर्म" },
        { id: 3,  emoji: "🔍", name: "कर्म-अकर्म-विकर्म" },
        { id: 4,  emoji: "🔥", name: "यज्ञाचे प्रकार" },
        { id: 5,  emoji: "✨", name: "ज्ञानाग्नी" },
        { id: 6,  emoji: "💎", name: "ज्ञानाची पवित्रता" },
        { id: 7,  emoji: "🌊", name: "श्रद्धा आणि संशय" },
        { id: 8,  emoji: "👁",  name: "पंडित समदर्शी" },
        { id: 9,  emoji: "🌈", name: "ये यथा मां प्रपद्यन्ते" },
        { id: 10, emoji: "🌟", name: "ज्ञानयोग — सार" }
      ]
    },
    {
      id: 5, number: "५", name: "कर्मसंन्यासयोग", emoji: "⚖️",
      available: true,
      summary: "संन्यास घ्यायचा की कर्म करायचे — या प्रश्नावर कृष्ण स्पष्ट उत्तर देतो. खरा संन्यास बाह्य नाही, आंतरिक आहे. कमळाच्या पाकळीसारखे जगात राहायचे पण जगाने स्पर्श होऊ द्यायचा नाही — हाच कर्मसंन्यासयोग. शरीर-मन-बुद्धी ही साधने आहेत, \"मी\" नाही — हे जाणणे म्हणजे खरी मुक्ती.",
      concepts: [
        { id: 1,  emoji: "⚖️", name: "संन्यास की कर्मयोग" },
        { id: 2,  emoji: "🔗", name: "सांख्य आणि योग" },
        { id: 3,  emoji: "🌿", name: "योगयुक्त विशुद्धात्मा" },
        { id: 4,  emoji: "🌸", name: "कर्मसंन्यासी" },
        { id: 5,  emoji: "🛠️", name: "शरीर-मन-बुद्धी" },
        { id: 6,  emoji: "🏰", name: "नवद्वारपुर" },
        { id: 7,  emoji: "⚡", name: "ईश्वर कर्ता नाही" },
        { id: 8,  emoji: "☀️", name: "ज्ञान हे सूर्यासारखे" },
        { id: 9,  emoji: "👁️", name: "समदृष्टी" },
        { id: 10, emoji: "🌅", name: "बाहेरचं सुख क्षणिक" },
        { id: 11, emoji: "⚔️", name: "काम-क्रोध जिंकणं" },
        { id: 12, emoji: "🕉️", name: "ब्रह्मनिर्वाण" }
      ]
    },
    {
      id: 6, number: "६", name: "ध्यानयोग", emoji: "🧘",
      available: false, concepts: []
    },
    {
      id: 7, number: "७", name: "ज्ञानविज्ञानयोग", emoji: "🔬",
      available: false, concepts: []
    },
    {
      id: 8, number: "८", name: "अक्षरब्रह्मयोग", emoji: "🕉️",
      available: false, concepts: []
    },
    {
      id: 9, number: "९", name: "राजविद्याराजगुह्ययोग", emoji: "👑",
      available: false, concepts: []
    },
    {
      id: 10, number: "१०", name: "विभूतियोग", emoji: "🌌",
      available: false, concepts: []
    },
    {
      id: 11, number: "११", name: "विश्वरूपदर्शनयोग", emoji: "🌍",
      available: false, concepts: []
    },
    {
      id: 12, number: "१२", name: "भक्तियोग", emoji: "❤️",
      available: false, concepts: []
    },
    {
      id: 13, number: "१३", name: "क्षेत्रक्षेत्रज्ञविभागयोग", emoji: "🏞️",
      available: false, concepts: []
    },
    {
      id: 14, number: "१४", name: "गुणत्रयविभागयोग", emoji: "⚗️",
      available: false, concepts: []
    },
    {
      id: 15, number: "१५", name: "पुरुषोत्तमयोग", emoji: "🌳",
      available: false, concepts: []
    },
    {
      id: 16, number: "१६", name: "दैवासुरसंपद्विभागयोग", emoji: "⚔️",
      available: false, concepts: []
    },
    {
      id: 17, number: "१७", name: "श्रद्धात्रयविभागयोग", emoji: "🙏",
      available: false, concepts: []
    },
    {
      id: 18, number: "१८", name: "मोक्षसंन्यासयोग", emoji: "🕊️",
      available: false, concepts: []
    }
  ]
};
