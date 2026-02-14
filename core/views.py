import json

from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_GET, require_http_methods

from core.models import Valentine
from core.utils import extract_youtube_id, check_rate_limit, get_client_ip


@csrf_exempt
@require_http_methods(["GET", "POST"])
def create_view(request):
    if request.method == "GET":
        return render(request, "core/create.html")

    # POST — create a valentine
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({"error": "Données invalides."}, status=400)

    sender_name = (data.get("senderName") or "").strip()[:50]
    recipient_name = (data.get("recipientName") or "").strip()[:50]
    acrostic_mode = data.get("acrosticMode", "default")
    custom_acrostic = data.get("customAcrostic")
    poem_mode = data.get("poemMode", "default")
    custom_poem = (data.get("customPoem") or "").strip()[:2000]
    music_mode = data.get("musicMode", "default")
    youtube_url = (data.get("youtubeUrl") or "").strip()

    if not sender_name or not recipient_name:
        return JsonResponse({"error": "Les prénoms sont obligatoires."}, status=400)

    if acrostic_mode not in ("default", "custom"):
        acrostic_mode = "default"
    if poem_mode not in ("default", "custom"):
        poem_mode = "default"
    if music_mode not in ("default", "youtube"):
        music_mode = "default"

    # Validate custom acrostic
    if acrostic_mode == "custom":
        if not isinstance(custom_acrostic, list) or len(custom_acrostic) != len(recipient_name):
            return JsonResponse({"error": "L'acrostiche doit avoir une phrase par lettre."}, status=400)
        for item in custom_acrostic:
            if not isinstance(item, dict) or not item.get("phrase", "").strip():
                return JsonResponse({"error": "Chaque ligne de l'acrostiche doit avoir une phrase."}, status=400)
    else:
        custom_acrostic = None

    if poem_mode != "custom":
        custom_poem = None

    # YouTube
    youtube_id = None
    if music_mode == "youtube":
        youtube_id = extract_youtube_id(youtube_url)
        if not youtube_id:
            return JsonResponse({"error": "Lien YouTube invalide."}, status=400)

    # Rate limit
    ip = get_client_ip(request)
    if not check_rate_limit(ip, recipient_name):
        return JsonResponse(
            {"error": "Tu as déjà envoyé 3 valentins aujourd'hui ! Reviens demain."},
            status=429,
        )

    valentine = Valentine.objects.create(
        sender_name=sender_name,
        recipient_name=recipient_name,
        acrostic_mode=acrostic_mode,
        custom_acrostic=custom_acrostic,
        poem_mode=poem_mode,
        custom_poem=custom_poem,
        music_mode=music_mode,
        youtube_id=youtube_id,
        sender_ip=ip,
    )

    return JsonResponse({"id": valentine.uid, "url": f"/v/{valentine.uid}/"})


@require_GET
def valentine_view(request, uid):
    valentine = get_object_or_404(Valentine, uid=uid)

    valentine_data = {
        "senderName": valentine.sender_name,
        "recipientName": valentine.recipient_name,
        "acrosticMode": valentine.acrostic_mode,
        "customAcrostic": valentine.custom_acrostic,
        "poemMode": valentine.poem_mode,
        "customPoem": valentine.custom_poem,
        "musicMode": valentine.music_mode,
        "youtubeId": valentine.youtube_id,
    }

    return render(request, "core/valentine.html", {
        "valentine_json": json.dumps(valentine_data, ensure_ascii=False),
    })
