from django.core.management.base import BaseCommand
from matches.utils.parsers import parse_football_matches, parse_basketball_matches
from matches.models import Match, Sport
from django.utils import timezone

class Command(BaseCommand):
    help = 'Парсинг матчей из внешних источников и обновление базы данных'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--sport',
            type=str,
            help='Спорт для парсинга (football, basketball, etc)',
        )
    
    def handle(self, *args, **options):
        self.stdout.write('🚀 Начинаем парсинг матчей...')
        
        sport_type = options.get('sport')
        
        # Получаем или создаем виды спорта
        football_sport, _ = Sport.objects.get_or_create(
            name='Футбол',
            defaults={'slug': 'football', 'icon': 'futbol', 'order': 1}
        )
        
        basketball_sport, _ = Sport.objects.get_or_create(
            name='Баскетбол',
            defaults={'slug': 'basketball', 'icon': 'basketball-ball', 'order': 2}
        )
        
        # Парсим матчи в зависимости от указанного вида спорта
        if not sport_type or sport_type == 'football':
            self.stdout.write('⚽ Парсим футбольные матчи...')
            football_matches = parse_football_matches()
            self.update_matches(football_sport, football_matches)
        
        if not sport_type or sport_type == 'basketball':
            self.stdout.write('🏀 Парсим баскетбольные матчи...')
            basketball_matches = parse_basketball_matches()
            self.update_matches(basketball_sport, basketball_matches)
        
        self.stdout.write(self.style.SUCCESS('✅ Парсинг завершен успешно!'))
    
    def update_matches(self, sport, matches_data):
        """Обновление или создание матчей"""
        for match_data in matches_data:
            try:
                # Создаем уникальный внешний ID если его нет
                external_id = match_data.get('external_id') or f"{sport.slug}_{match_data['team1']}_{match_data['team2']}_{match_data['start_time'].timestamp()}"
                
                match, created = Match.objects.update_or_create(
                    sport=sport,
                    external_id=external_id,
                    defaults={
                        'team1': match_data['team1'],
                        'team2': match_data['team2'],
                        'team1_logo': match_data.get('team1_logo', ''),
                        'team2_logo': match_data.get('team2_logo', ''),
                        'start_time': match_data['start_time'],
                        'league': match_data['league'],
                        'country': match_data.get('country', ''),
                        'coefficient_team1': match_data['coefficient_team1'],
                        'coefficient_team2': match_data['coefficient_team2'],
                        'coefficient_draw': match_data.get('coefficient_draw'),
                        'total_over': match_data.get('total_over'),
                        'total_under': match_data.get('total_under'),
                        'status': match_data['status'],
                        'is_active': True,
                    }
                )
                
                if created:
                    self.stdout.write(f'✅ Создан матч: {match}')
                else:
                    self.stdout.write(f'🔄 Обновлен матч: {match}')
                    
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'❌ Ошибка при обработке матча: {e}'))