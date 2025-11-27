library(worldfootballR)
library(dplyr)
library(purrr)
library(readr)

leagues <- c("BEL", "MEX", "NED", "POR")  
seasons <- 2023:2025
stat_types <- c(
  "standard",
  "shooting",
  "passing",
  "defense",
  "misc",
  "keepers"
)
team_or_player <- "player"
output_dir <- "data_exports"

if (!dir.exists(output_dir)) {
  dir.create(output_dir)
}

fetch_and_save_stats <- function(league, stat_type) {
  message(paste0(">> Fetching ", stat_type, " stats for ", league, " ..."))
  
  league_data <- map_df(seasons, function(season_year) {
    Sys.sleep(3)  
    tryCatch(
      {
        df <- fb_league_stats(
          country = league,
          gender = "M",
          season_end_year = season_year,
          stat_type = stat_type,
          team_or_player = team_or_player
        )
        df$Season <- season_year
        return(df)
      },
      error = function(e) {
        message(paste("  ❌ Failed for", league, "season", season_year, "stat:", stat_type))
        return(NULL)
      }
    )
  })
  
  if (!is.null(league_data) && nrow(league_data) > 0) {
    file_name <- paste0(output_dir, "/", league, "_", stat_type, ".csv")
    write_csv(league_data, file_name)
    message(paste0("  ✅ Saved: ", file_name, " (", nrow(league_data), " rows)"))
  } else {
    message(paste0("  ⚠️ No data found for ", league, " - ", stat_type))
  }
}

walk(leagues, function(league) {
  walk(stat_types, function(stat_type) {
    fetch_and_save_stats(league, stat_type)
  })
})
