import random
from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.db.models import Count
from .models import Card, Category


def get_context_with_categories(request, selected_category_id=None):
    """Общий контекст со списком всех тематик."""
    from django.db.models import Q
    categories = Category.objects.annotate(
        words_count=Count('cards', filter=Q(cards__group=1), distinct=True)
    ).order_by('-id')  # Сортировка по убыванию ID (новые первыми)
    return {
        'categories': categories,
        'selected_category_id': selected_category_id,
    }


def get_last_non_empty_category():
    """Возвращает последнюю непустую тематику (с карточками группы 1)."""
    from django.db.models import Q
    last_category = Category.objects.annotate(
        words_count=Count('cards', filter=Q(cards__group=1), distinct=True)
    ).filter(words_count__gt=0).order_by('-id').first()
    return last_category


def practice(request):
    category_id = request.GET.get('category')
    selected_category = None
    
    # Если категория не выбрана, пробуем выбрать последнюю непустую
    if not category_id:
        last_category = get_last_non_empty_category()
        if last_category:
            # Перенаправляем на эту категорию
            return redirect(f'{request.path}?category={last_category.id}')
    
    if category_id:
        selected_category = get_object_or_404(Category, id=category_id)
        cards = Card.objects.filter(category=selected_category)
    else:
        cards = Card.objects.all()
    
    if not cards.exists():
        context = {'no_cards': True}
        context.update(get_context_with_categories(request, category_id))
        return render(request, 'cards/practice.html', context)

    # Группируем карточки по группам
    groups = {1: [], 2: [], 3: [], 4: []}
    for card in cards:
        groups[card.group].append(card)

    non_empty_groups = [g for g in groups if groups[g]]
    if not non_empty_groups:
        context = {'no_cards': True}
        context.update(get_context_with_categories(request, category_id))
        return render(request, 'cards/practice.html', context)

    total_cards = len(cards)
    group1_count = len(groups[1])
    half_total = total_cards / 2

    # Если карточек группы 1 >= половины от общего числа, показываем только их
    if group1_count >= half_total:
        chosen_group = 1
    else:
        # Иначе используем вероятностный алгоритм
        group_probs = {1: 0.6, 2: 0.2, 3: 0.15, 4: 0.05}
        total_prob = sum(group_probs[g] for g in non_empty_groups)
        adjusted_probs = {g: group_probs[g] / total_prob for g in non_empty_groups}
        chosen_group = random.choices(
            population=non_empty_groups,
            weights=[adjusted_probs[g] for g in non_empty_groups]
        )[0]

    current_card = random.choice(groups[chosen_group])

    correct_translation = current_card.translation

    # Собираем неправильные варианты из других карточек
    other_cards = [c for c in cards if c.id != current_card.id]
    other_translations = [c.translation for c in other_cards]

    num_needed = 3
    if len(other_translations) < num_needed:
        # Если недостаточно вариантов, берём с повторами
        selected_other = random.choices(other_translations, k=num_needed)
    else:
        selected_other = random.sample(other_translations, num_needed)

    options = [correct_translation] + selected_other
    random.shuffle(options)

    context = {
        'card': current_card,
        'options': options,
        'selected_category': selected_category,
    }
    context.update(get_context_with_categories(request, category_id))
    return render(request, 'cards/practice.html', context)


def check_answer(request):
    if request.method == 'POST':
        card_id = request.POST.get('card_id')
        selected = request.POST.get('selected')
        card = get_object_or_404(Card, id=card_id)

        is_correct = selected == card.translation

        if is_correct:
            if card.group < 4:
                card.group += 1
        else:
            if card.group > 1:
                card.group -= 1
        card.save()

        correct_translation = card.translation

        return JsonResponse({
            'correct': is_correct,
            'new_group': card.group,
            'message': 'Правильно!' if is_correct else f'Неправильно. Правильный перевод: {correct_translation}'
        })
    return JsonResponse({'error': 'Method not allowed'}, status=405)


def learn(request):
    category_id = request.GET.get('category')
    selected_category = None
    
    # Если категория не выбрана, пробуем выбрать последнюю непустую
    if not category_id:
        last_category = get_last_non_empty_category()
        if last_category:
            # Перенаправляем на эту категорию
            return redirect(f'{request.path}?category={last_category.id}')
    
    if category_id:
        selected_category = get_object_or_404(Category, id=category_id)
    
    context = {
        'selected_category': selected_category,
    }
    context.update(get_context_with_categories(request, category_id))
    return render(request, 'cards/learn.html', context)


def next_learn_card(request):
    card_id = request.GET.get('card_id')
    category_id = request.GET.get('category')
    
    if not card_id:
        return JsonResponse({'error': 'card_id parameter required'}, status=400)
    
    # Если указана категория, проверяем что карточка принадлежит ей
    card = get_object_or_404(Card, id=card_id)
    if category_id and card.category_id != int(category_id):
        return JsonResponse({'error': 'Card not in selected category'}, status=403)
    
    data = {
        'id': card.id,
        'word': card.word,
        'translation': card.translation,
        'image_url': card.image.url if card.image else None,
    }
    return JsonResponse(data)


def get_group1_cards(request):
    category_id = request.GET.get('category')
    
    if category_id:
        cards = Card.objects.filter(group=1, category_id=category_id).values_list('id', flat=True)
    else:
        cards = Card.objects.filter(group=1).values_list('id', flat=True)
    
    card_ids = list(cards)
    if not card_ids:
        return JsonResponse({'error': 'Нет карточек в группе 1'})
    random.shuffle(card_ids)
    return JsonResponse({'card_ids': card_ids})