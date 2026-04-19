/**
 * stories.js
 * ----------
 * GITA_STORIES[adhyayId][conceptId] — structured story data for the कथा tab.
 *
 * Story format:
 *   shloka        — { ref, text (\n for line breaks), meaning }
 *   conceptSummary — plain text intro paragraph
 *   story          — { scene, characters[], body[], turningPoint, gitaConnect,
 *                       reflection, sankalp }
 *
 * body items: { type: "para", text } | { type: "dialogue", speaker, text }
 * gitaConnect may contain <span class="story-highlight">…</span>
 * turningPoint/sankalp may contain <strong>…</strong>
 *
 * Add a new entry here whenever a story is ready for a concept.
 * Concepts without an entry → कथा tab is hidden (zero regression).
 */

const GITA_STORIES = {

  1: {
    "1": {
      shloka: {
        ref: "गीता १.१",
        text: "धर्मक्षेत्रे कुरुक्षेत्रे समवेता युयुत्सवः ।\nमामकाः पाण्डवाश्चैव किमकुर्वत सञ्जय ।।",
        meaning: "\"हे संजय, धर्माच्या क्षेत्रावर — कुरुक्षेत्रावर — एकत्र आलेले <em>माझे</em> आणि पांडवांचे युद्धेच्छू — त्यांनी काय केले?\""
      },
      conceptSummary: "गीतेचा पहिला शब्द <strong>\"धर्म\"</strong> आणि पहिला भाव <strong>\"मामकाः — माझे\"</strong>. धृतराष्ट्र म्हणतो — <em>\"माझे\"</em> आणि <em>\"त्यांचे\"</em>. हा एकच भेद — महाभारताचे मूळ आहे. जिथे <strong>\"माझे\"</strong> येते — तिथे संघर्ष जन्मतो. जिथे संघर्ष येतो — तिथे धर्माचा प्रश्न उद्भवतो.",
      story: {
        scene: {
          emoji: "🏠",
          title: "वडिलांची संपत्ती — दोन भावांचा वाद",
          subtitle: "पुण्यातील एका मध्यमवर्गीय कुटुंबात"
        },
        characters: [
          { emoji: "👨", role: "रमेश", desc: "थोरला भाऊ" },
          { emoji: "👦", role: "सुरेश", desc: "धाकटा भाऊ" },
          { emoji: "👴", role: "आप्पा", desc: "वडील (नुकतेच निवर्तले)" },
          { emoji: "👩", role: "सुमनताई", desc: "रमेशची पत्नी" }
        ],
        body: [
          {
            type: "para",
            text: "आप्पा गेले — त्याला तीन महिने उलटले. कात्रज-देहूरोड परिसरातील त्यांचे जुने घर, थोडी जमीन, आणि बँकेत असलेली थोडीशी ठेव — एवढीच संपत्ती मागे राहिली. रमेश आणि सुरेश — दोन्ही भाऊ — एकाच घरात लहानाचे मोठे झालेले. आईने दोघांनाही सारखेच सांभाळलेले."
          },
          {
            type: "para",
            text: "पण आप्पा गेल्यावर एक महिन्यात — घर बदलले. रमेशची पत्नी सुमनताई म्हणाल्या, <em>\"जमीन माझ्या नावावर व्हायला हवी — मीच इतकी वर्षे सेवा केली.\"</em> सुरेशला राग आला. तो म्हणाला, <em>\"माझाही हक्क आहे.\"</em>"
          },
          {
            type: "dialogue",
            speaker: "रमेश → सुरेश",
            text: "\"हे घर माझ्या कष्टाने टिकले. मी आप्पांची सेवा केली. <strong>माझा</strong> हक्क जास्त आहे.\""
          },
          {
            type: "dialogue",
            speaker: "सुरेश → रमेश",
            text: "\"आप्पांनी कधी सांगितले नाही की हे फक्त तुझे आहे. <strong>माझेही</strong> तेवढेच आहे.\""
          },
          {
            type: "para",
            text: "आता वकील आले. नातेवाईक मध्ये पडले. आईला दोन्ही बाजूंनी फोन येऊ लागले. जे घर कधी हास्याने भरलेले होते — ते आता न्यायालयाच्या कागदपत्रांनी भरले."
          }
        ],
        turningPoint: "आईने एक दिवस दोघांना बोलावले. शांतपणे म्हणाली —<br><br><em>\"रमेश, तू 'माझे' म्हणतोस. सुरेश, तूही 'माझे' म्हणतोस. पण हे घर आप्पांनी बांधले — ते कधी म्हणाले नाहीत की हे 'माझे' आहे. ते नेहमी म्हणायचे — <strong>'आपले घर'</strong>.\"</em><br><br>त्या दिवशी दोघेही गप्प बसले. <strong>\"माझे\"</strong> या एका शब्दाने — दोन सख्ख्या भावांत युद्ध निर्माण केले होते.",
        gitaConnect: "धृतराष्ट्र म्हणतो — <span class=\"story-highlight\">\"मामकाः\"</span> — माझे. त्याच एका शब्दाने महाभारत घडले.<br><br>रमेश आणि सुरेश — दोघेही धृतराष्ट्रासारखेच \"माझे\" म्हणत होते. <span class=\"story-highlight\">\"माझे\" हा भाव येताच — दुसरा \"ते\" होतो. \"ते\" झाले की संघर्ष अटळ असतो.</span><br><br>गीता सांगते — संघर्षाचे मूळ परिस्थितीत नाही, माणसांत नाही — <span class=\"story-highlight\">ममत्वाच्या भावात आहे.</span>",
        reflection: "\"माझ्या घरात, कामाच्या ठिकाणी — कुठे 'माझे' हा भाव संघर्षाचे कारण बनला आहे?\"",
        sankalp: "एका प्रसंगात <strong>\"माझे\"</strong> ऐवजी <strong>\"आपले\"</strong> म्हणून पाहा — आणि संघर्ष कसा विरतो ते जाणा."
      }
    }
  }

  // ── Add more adhyays / concepts here as stories are written ──────
  // Pattern: GITA_STORIES[adhyayId]["conceptId"] = { shloka, conceptSummary, story }

};
