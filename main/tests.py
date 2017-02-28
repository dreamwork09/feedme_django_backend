from django.test import TestCase
from main.models import Restaurant
from main.lib import weekdays


class TestRestaurant(TestCase):
    fixtures = ['main/fixtures/all_fixtures_exclude_likes.json']

    def test_openingtimes(self):
        for rest in Restaurant.objects.all():
            tup_list = rest.get_displayable_opening_times()
            prev_day_tup = (0, )
            prev_tup = (0, )
            day_flags = {'mon': False, 'tue': False, 'wed': False, 'thu': False,
                         'fri': False, 'sat': False, 'sun': False}
            for tup in tup_list:
                if prev_tup[0] != tup[0]:
                    prev_day_tup = prev_tup
                if prev_day_tup[0] != 0:
                    self.assertEqual(prev_day_tup[0], weekdays.prev(tup[0])[1])
                day_flags[weekdays.to_shortcode(tup[0])] = True
                prev_tup = tup
            for flag in list(day_flags.values()):
                self.assertTrue(flag)
