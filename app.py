import streamlit as st
import re
from google import genai
from google.genai import types

st.set_page_config(
    page_title="AI Story & Video Scene Generator",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------- Styling ----------
st.markdown("""
<style>
    .main-title {
        font-size: 2.2rem;
        font-weight: 800;
        margin-bottom: 0.2rem;
    }
    .subtitle {
        color: #6b7280;
        margin-bottom: 1.4rem;
    }
    .scene-card {
        border: 1px solid rgba(128,128,128,.25);
        border-radius: 12px;
        padding: 14px 16px;
        margin: 8px 0;
    }
    .small-note {
        color: #6b7280;
        font-size: .88rem;
    }
</style>
""", unsafe_allow_html=True)

# ---------- Helpers ----------
def get_api_key():
    try:
        return st.secrets["GEMINI_API_KEY"]
    except Exception:
        return None


def build_prompt(genre, duration, character_count, language, style, custom_topic=""):
    genre_text = custom_topic.strip() if genre == "Custom" and custom_topic.strip() else genre

    return f"""
You are an expert AI Video Story & Scene Director.

Create a complete original story designed specifically to be converted into an AI-generated video.

USER CONFIGURATION
- Genre / Topic: {genre_text}
- Total video duration: {duration} seconds
- Number of characters: {character_count}
- Dialogue language: {language}
- Story style: {style}

IMPORTANT RULES

1. The story must have a clear beginning, middle, climax/development, and satisfying ending.
2. Divide the story into multiple scenes whose durations add up EXACTLY to {duration} seconds.
3. Choose a sensible number of scenes based on the total duration. For very short videos, use fewer scenes; for longer videos, use more scenes.
4. Every scene must logically continue from the previous scene. Do not create unrelated scenes.
5. Create EXACTLY {character_count} main characters. Do not introduce additional named speaking characters.
6. Define every character completely BEFORE the scene list.
7. Character appearance must remain consistent in every scene. When a character appears again, repeat the important fixed appearance details so the output can be used as an AI-video prompt.
8. Clothing, hairstyle, accessories, age, body type, and other fixed visual traits should not randomly change.
9. Locations, props, weather, lighting, and time of day should remain consistent unless the story explicitly changes them.
10. Make every scene visually clear and useful for AI video generation.
11. Dialogue should be natural and short enough to fit the scene duration.
12. Do not use Google Search, web search, external research, or outside information. Create the story yourself.
13. Do not generate a video. Generate only the story and detailed scene instructions.

DIALOGUE RULES
- If language is English: provide English dialogue only.
- If language is Urdu: provide natural Urdu dialogue in Urdu script only.
- If language is Both English & Urdu: provide both versions for every spoken line.
- Keep Urdu natural and conversational, not word-for-word machine translation.

OUTPUT FORMAT

STORY TITLE:
[title]

GENRE:
[genre]

TOTAL DURATION:
{duration} seconds

NUMBER OF CHARACTERS:
{character_count}

DIALOGUE LANGUAGE:
{language}

STORY SUMMARY:
[2-5 sentence summary]

CHARACTERS:

CHARACTER 1 — [Name]
- Age:
- Gender:
- Physical appearance:
- Face:
- Hair:
- Skin tone:
- Clothing:
- Accessories:
- Personality:
- Voice style:

Continue until exactly {character_count} characters are defined.

SCENES:

SCENE 01 — [start]–[end] seconds
- Location / Environment:
- Time of Day:
- Characters Present:
- Character Appearance:
- Action:
- Facial Expressions:
- Body Language:
- Camera Shot:
- Camera Movement:
- Background / Visual Details:
- Narration:
- Dialogue:
- Sound Effects:
- Music / Mood:
- Transition:

Repeat this exact structure for every scene.

FINAL CONTINUITY NOTES:
- Character consistency:
- Important props:
- Location continuity:
- Visual style:
- Ending state:

Do not add commentary about these instructions. Return only the requested story.
"""


def generate_story(prompt):
    api_key = get_api_key()
    if not api_key:
        raise RuntimeError(
            "Gemini API key is missing. Add GEMINI_API_KEY to Streamlit Secrets."
        )

    client = genai.Client(api_key=api_key)

    response = client.models.generate_content(
        model="gemini-3.6-flash",
        contents=prompt,
        config=types.GenerateContentConfig(
            temperature=0.9,
            max_output_tokens=12000,
        ),
    )

    text = getattr(response, "text", None)
    if not text:
        raise RuntimeError("Gemini returned an empty response.")

    return text.strip()


def extract_section(text, heading, next_heading=None):
    pattern = rf"(?is){re.escape(heading)}\s*:?\s*(.*)"
    match = re.search(pattern, text)
    if not match:
        return ""
    content = match.group(1)
    if next_heading:
        content = re.split(
            rf"(?is)\n\s*{re.escape(next_heading)}\s*:?", content, maxsplit=1
        )[0]
    return content.strip()


# ---------- Header ----------
st.markdown('<div class="main-title">🎬 AI Story & Video Scene Generator</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="subtitle">Configure your story, then let Gemini create a video-ready scene plan.</div>',
    unsafe_allow_html=True,
)

# ---------- Sidebar configuration ----------
with st.sidebar:
    st.header("⚙️ Story Configuration")

    genre = st.selectbox(
        "Story Topic / Genre",
        [
            "Horror",
            "Romantic",
            "Funny / Comedy",
            "Action",
            "Adventure",
            "Mystery",
            "Thriller",
            "Fantasy",
            "Emotional",
            "Sci-Fi",
            "Custom",
        ],
    )

    custom_topic = ""
    if genre == "Custom":
        custom_topic = st.text_input(
            "Enter your custom topic",
            placeholder="e.g. A mysterious train journey",
        )

    duration_choice = st.selectbox(
        "Total Video Duration",
        ["15 seconds", "30 seconds", "45 seconds", "60 seconds",
         "90 seconds", "120 seconds", "Custom"],
    )

    if duration_choice == "Custom":
        duration = st.number_input(
            "Custom duration (seconds)",
            min_value=5,
            max_value=600,
            value=60,
            step=5,
        )
    else:
        duration = int(duration_choice.split()[0])

    character_choice = st.selectbox(
        "Number of Characters",
        ["1", "2", "3", "4", "5", "6", "Custom"],
    )

    if character_choice == "Custom":
        character_count = st.number_input(
            "Custom number of characters",
            min_value=1,
            max_value=12,
            value=2,
            step=1,
        )
    else:
        character_count = int(character_choice)

    language = st.radio(
        "Dialogue Language",
        ["English", "Urdu", "Both English & Urdu"],
    )

    style = st.selectbox(
        "Story Style",
        [
            "Cinematic",
            "Realistic",
            "Funny",
            "Dark",
            "Emotional",
            "Dramatic",
            "Fast-paced",
            "Suspenseful",
        ],
    )

    st.divider()
    st.markdown(
        '<div class="small-note">🔐 Your Gemini API key is read from Streamlit Secrets and is not stored in this app.</div>',
        unsafe_allow_html=True,
    )

# ---------- Validation ----------
if genre == "Custom" and not custom_topic.strip():
    st.info("Enter a custom topic in the sidebar to continue.")

# ---------- Generate ----------
generate = st.button(
    "✨ Generate Story",
    type="primary",
    use_container_width=True,
)

if generate:
    if not get_api_key():
        st.error(
            "GEMINI_API_KEY is not configured. In Streamlit Cloud, open "
            "App Settings → Secrets and add your Gemini API key."
        )
        st.stop()

    if genre == "Custom" and not custom_topic.strip():
        st.error("Please enter your custom story topic.")
        st.stop()

    prompt = build_prompt(
        genre=genre,
        duration=duration,
        character_count=character_count,
        language=language,
        style=style,
        custom_topic=custom_topic,
    )

    try:
        with st.spinner("🎬 Creating your story and scene plan..."):
            story = generate_story(prompt)

        st.session_state["story"] = story
        st.session_state["config"] = {
            "genre": custom_topic.strip() if genre == "Custom" else genre,
            "duration": duration,
            "characters": character_count,
            "language": language,
            "style": style,
        }
        st.success("Story generated successfully!")

    except Exception as e:
        error_text = str(e)
        if "API_KEY" in error_text.upper() or "INVALID" in error_text.upper():
            st.error("The Gemini API key appears to be invalid or unavailable.")
        else:
            st.error(f"Gemini/API error: {error_text}")

# ---------- Output ----------
if "story" in st.session_state:
    story = st.session_state["story"]
    cfg = st.session_state["config"]

    st.divider()
    st.subheader("📖 Story Overview")

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Genre", cfg["genre"])
    c2.metric("Duration", f'{cfg["duration"]} sec')
    c3.metric("Characters", cfg["characters"])
    c4.metric("Language", cfg["language"])

    summary = extract_section(story, "STORY SUMMARY", "CHARACTERS")
    characters = extract_section(story, "CHARACTERS", "SCENES")
    scenes = extract_section(story, "SCENES", "FINAL CONTINUITY NOTES")
    continuity = extract_section(story, "FINAL CONTINUITY NOTES")

    title_match = re.search(r"(?im)^STORY TITLE:\s*(.+)$", story)
    title = title_match.group(1).strip() if title_match else "Generated Story"

    st.subheader(f"🎞️ {title}")

    if summary:
        with st.expander("📝 Story Summary", expanded=True):
            st.write(summary)

    if characters:
        with st.expander("👥 Characters", expanded=True):
            st.markdown(characters)

    if scenes:
        with st.expander("🎬 Scene-by-Scene Video Plan", expanded=True):
            # Keep scene headings visually separated.
            parts = re.split(r"(?im)(?=^SCENE\s+\d+\s*[—-])", scenes.strip())
            for part in parts:
                part = part.strip()
                if not part:
                    continue
                heading_match = re.match(r"(?im)^(SCENE\s+\d+\s*[—-].*)$", part)
                if heading_match:
                    heading = heading_match.group(1).strip()
                    body = part[len(heading):].strip()
                    st.markdown(f"#### {heading}")
                    st.markdown(body)
                    st.divider()
                else:
                    st.markdown(part)

    if continuity:
        with st.expander("🔄 Final Continuity Notes"):
            st.markdown(continuity)

    st.subheader("📤 Export")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.download_button(
            "⬇️ Download TXT",
            data=story,
            file_name="ai_story_video_scene_plan.txt",
            mime="text/plain",
            use_container_width=True,
        )

    with col2:
        if st.button("🔄 Generate Again", use_container_width=True):
            prompt = build_prompt(
                genre=genre,
                duration=duration,
                character_count=character_count,
                language=language,
                style=style,
                custom_topic=custom_topic,
            )
            try:
                with st.spinner("Creating a new version..."):
                    new_story = generate_story(prompt)
                st.session_state["story"] = new_story
                st.rerun()
            except Exception as e:
                st.error(f"Gemini/API error: {e}")

    with col3:
        if st.button("🗑️ Clear", use_container_width=True):
            st.session_state.pop("story", None)
            st.session_state.pop("config", None)
            st.rerun()

    st.caption(
        "Tip: The generated scene descriptions are designed as a planning/prompt layer "
        "for a separate AI video-generation workflow."
    )
else:
    st.info(
        "👈 Choose your genre, duration, characters, dialogue language, and style, "
        "then click **Generate Story**."
    )
