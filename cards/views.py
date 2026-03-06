import random
from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from .models import Card

def practice(request):
    cards = Card.objects.all()
    if not cards.exists():
        return render(request, 'cards/practice.html', {'no_cards': True})

    # Группируем карточки по группам
    groups = {1: [], 2: [], 3: [], 4: []}
    for card in cards:
        groups[card.group].append(card)

    # Исходные вероятности для групп
    group_probs = {1: 0.6, 2: 0.2, 3: 0.15, 4: 0.05}

    # Определяем непустые группы
    non_empty_groups = [g for g in groups if groups[g]]
    if not non_empty_groups:
        return render(request, 'cards/practice.html', {'no_cards': True})

    # Пересчитываем вероятности для непустых групп
    total_prob = sum(group_probs[g] for g in non_empty_groups)
    adjusted_probs = {g: group_probs[g] / total_prob for g in non_empty_groups}

    # Выбираем группу с учётом скорректированных вероятностей
    chosen_group = random.choices(
        population=non_empty_groups,
        weights=[adjusted_probs[g] for g in non_empty_groups]
    )[0]

    # Выбираем случайную карточку из выбранной группы
    current_card = random.choice(groups[chosen_group])

    # Формируем варианты ответа
    correct_translations = current_card.get_translations()
    correct_translation = random.choice(correct_translations)

    # Собираем переводы из других карточек
    other_cards = [c for c in cards if c.id != current_card.id]
    other_translations = []
    for card in other_cards:
        other_translations.extend(card.get_translations())

    # Выбираем 3 случайных перевода из других карточек
    num_needed = 3
    if len(other_translations) < num_needed:
        selected_other = random.choices(other_translations, k=num_needed)
    else:
        selected_other = random.sample(other_translations, num_needed)

    # Перемешиваем варианты
    options = [correct_translation] + selected_other
    random.shuffle(options)

    context = {
        'card': current_card,
        'options': options,
    }
    return render(request, 'cards/practice.html', context)


def check_answer(request):
    
    

    if request.method == 'POST':
        card_id = request.POST.get('card_id')
        selected = request.POST.get('selected')
        card = get_object_or_404(Card, id=card_id)

        is_correct = selected in card.get_translations()

        if is_correct:
            if card.group < 4:
                card.group += 1
        else:
            if card.group > 1:
                card.group -= 1
        card.save()

        correct_translation = card.translation1  # для сообщения

        return JsonResponse({
            'correct': is_correct,
            'new_group': card.group,
            'message': 'Правильно!' if is_correct else f'Неправильно. Правильный перевод: {correct_translation}'
        })
    return JsonResponse({'error': 'Method not allowed'}, status=405)


def learn(request):
    # Получаем все карточки из группы 1
    cards_group1 = Card.objects.filter(group=1)
    if not cards_group1.exists():
        return render(request, 'cards/learn.html', {'no_cards': True})
    
    # Выбираем случайную карточку
    card = random.choice(cards_group1)
    
    context = {
        'card': card,
    }
    return render(request, 'cards/learn.html', context)