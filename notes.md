Example Invocations
-------------------
GetForecast can I go flying in {Location}
GetForecast can I go flying at {Location}
GetForecast can I fly at {Location}
GetForecast can I fly in {Location}
GetForecast can I go flying in {Location} on {Date}
GetForecast can I go flying at {Location} on {Date}
GetForecast can I go flying in {Location} {Date}
GetForecast can I go flying at {Location} {Date}
GetForecast can I fly at {Location} on {Date}
GetForecast can I fly in {Location} on {Date}
GetForecast on {Date} can i go flying in {Location}
GetForecast on {Date} can i go flying at {Location}
GetForecast can i go flying
GetForecast can i go flying on {Date}
GetForecast can i fly on {Date}
GetForecast can i fly
GetForecast can i fly {Location} {Date}

Date Logic
----------
if there's no date: currently
if its between now and 24 hours: hourly
if it's > 24 hours < 7 days: daily
if it's > 7 days: exception
