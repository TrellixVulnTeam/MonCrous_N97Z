# Copyright 2008-2010 Yousef Ourabi

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at

# http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


import datetime
import django.db.models
from django.db.models.signals import post_save
from django.core.cache import cache

BANISH_PREFIX = 'DJANGO_BANISH:'


class Banishment(django.db.models.Model):
    id = django.db.models.AutoField(primary_key=True)

    # Flush out time constrained banned in future revisions
    # ban_start = models.DateField(help_text="Banish Start Date.")
    # ban_stop = models.DateField(help_text="Banish Stop Date.")
    # ban_is_permanent = models.BooleanField(help_text="Is Ban Permanent? (Start/Stop ignored)")

    ban_reason = django.db.models.CharField(max_length=255, help_text="Reason for the ban?")

    BAN_TYPES = (
        ('ip-address', 'IP Address'),
        ('user-agent', 'User Agent'),
    )

    type = django.db.models.CharField(
        max_length=20,
        choices=BAN_TYPES,
        default=0,
        help_text="Type of User Ban to store"
    )

    condition = django.db.models.CharField(
        max_length=255,
        help_text='Some descriptive text goes here'
    )

    def __unicode__(self):
        return "Banished %s %s " % (self.type, self.condition)

    def __str__(self):
        return self.__unicode__()

    def is_current(self):
        """
        Determine if this banishment is current by comparing
        dates
        """
        if self.permanent or self.stop > datetime.date.today(): 
            return True
        return False

    class Meta:
        permissions = (("can_ban_user", "Can Ban User"),)
        verbose_name = "Banishments"
        verbose_name_plural = "Banishments"
        db_table = 'banishments'


def _update_cache(sender, instance, **kwargs):
     if instance.type == 'ip-address':
        cache_key = BANISH_PREFIX + instance.condition
        cache.set(cache_key, "1")  

post_save.connect(_update_cache, sender=Banishment)
