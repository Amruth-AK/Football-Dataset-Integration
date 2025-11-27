library(worldfootballR)

big5_standard <- fb_big5_advanced_season_stats(
  season_end_year = 2023:2025,
  team_or_player = "player",
  stat_type = "standard",
  time_pause = 5
)

big5_shooting <- fb_big5_advanced_season_stats(
  season_end_year = 2023:2025,
  team_or_player = "player",
  stat_type = "shooting",
  time_pause = 5
)

big5_passing <- fb_big5_advanced_season_stats(
  season_end_year = 2023:2025,
  team_or_player = "player",
  stat_type = "passing",
  time_pause = 5
)

big5_defense <- fb_big5_advanced_season_stats(
  season_end_year = 2023:2025,
  team_or_player = "player",
  stat_type = "defense",
  time_pause = 5
)

big5_misc <- fb_big5_advanced_season_stats(
  season_end_year = 2023:2025,
  team_or_player = "player",
  stat_type = "misc",
  time_pause = 5
)

big5_keepers <- fb_big5_advanced_season_stats(
  season_end_year = 2023:2025,
  team_or_player = "player",
  stat_type = "keepers",
  time_pause = 5
)

# Write all data frames to CSV
write.csv(big5_standard, "big5_standard.csv", row.names = FALSE)
write.csv(big5_shooting, "big5_shooting.csv", row.names = FALSE)
write.csv(big5_passing, "big5_passing.csv", row.names = FALSE)
write.csv(big5_defense, "big5_defense.csv", row.names = FALSE)
write.csv(big5_misc, "big5_misc.csv", row.names = FALSE)
write.csv(big5_keepers, "big5_keepers.csv", row.names = FALSE)