class APIQuery:
    # First, update the ChannelDesc class in datatype.py

    class ChannelDesc:
        def __init__(
            self,
            channel_number=None,
            title=None,
            is_audio=None,
            is_adult=None,
            station_id=None,
            min_length=None,
            max_length=None,
            select_alpha=False,
            select_random=False,
            first_channel=None,
            last_channel=None,
            size=1,
            limiter=None,
            exclude_channel_number=None,
            exclude_channel_numbers=None,
            exclude_first_last=False,
        ):
            self.channel_number = channel_number
            self.title = title
            self.is_audio = is_audio
            self.is_adult = is_adult
            self.station_id = station_id
            self.min_length = min_length
            self.max_length = max_length
            self.select_alpha = select_alpha
            self.select_random = select_random
            self.first_channel = first_channel  # Store first channel parameter
            self.last_channel = last_channel  # Store last channel parameter
            self.size = size if size > 0 else 1
            self.limiter = (limiter,)  # Placeholder for limiter if needed in future
            self.exclude_channel_number = (
                exclude_channel_number  # Store single exclude parameter
            )
            self.exclude_channel_numbers = (
                exclude_channel_numbers or []
            )  # Store list of exclude parameters
            self.exclude_first_last = exclude_first_last

        def __repr__(self) -> str:
            statement = "ChannelDesc DETAILS: \n"
            if self.channel_number is not None:
                statement += f"Channel Number: {self.channel_number}\n"
            if self.title is not None:
                statement += f"Title: {self.title}\n"
            if self.is_audio is not None:
                statement += f"Is Audio: {self.is_audio}\n"
            if self.is_adult is not None:
                statement += f"Is Adult: {self.is_adult}\n"
            if self.station_id is not None:
                statement += f"Station ID: {self.station_id}\n"
            if self.min_length is not None:
                statement += f"Min Length: {self.min_length}\n"
            if self.max_length is not None:
                statement += f"Max Length: {self.max_length}\n"
            if self.select_alpha is not None:
                statement += f"Filter Titles: {self.select_alpha}\n"
            if self.select_random is not None:
                statement += f"Select Random: {self.select_random}\n"
            if self.first_channel is not None:
                statement += f"First Channel: {self.first_channel}\n"
            if self.last_channel is not None:
                statement += f"Last Channel: {self.last_channel}\n"
            if self.exclude_channel_number is not None:
                statement += f"Exclude Channel Number: {self.exclude_channel_number}\n"
            if self.limiter is not None:
                statement += f"Limiter: {self.limiter}\n"
            if self.exclude_channel_numbers:
                statement += (
                    f"Exclude Channel Numbers: {self.exclude_channel_numbers}\n"
                )
            if self.exclude_first_last:
                statement += (
                    f"Exclude First and Last Channels: {self.exclude_first_last}\n"
                )
            statement += f"Size: {self.size}\n"
            return statement

    class Channel:
        def __init__(
            self,
            channel_number=None,
            station_id=None,
            title=None,
            is_adult=None,
            genres=None,
            channel_logo=None,
            cta=None,
            media_pid=None,
            is_catchup_enabled=None,
            is_restricted=None,
            entitlements=None,
            is_free_to_air=None,
            is_audio=None,
            dt_channel_number=None,
            channel_id=None,
            quality=None,
            distribution_types=None,
            distribution_urls=None,
            is_iptv=False,
            type=None,
            lowLatency=None,
            video_src_dash=None,
            video_src_m3u=None,
            pid_dash=None,
            pid_m3u=None,
            is_subscribed=None,
            description=None,
        ):
            """
            Initialize a Channel instance with various attributes related to channel information.

            Args:
                channel_number (Optional[int]): The channel number.
                station_id (Optional[str]): The station identifier.
                title (Optional[str]): The title of the channel.
                is_adult (Optional[bool]): Whether the channel is for adult content.
                genres (Optional[List[str]]): A list of genres the channel belongs to.
                channel_logo (Optional[str]): The URL or path to the channel logo.
                cta (Optional[str]): Call to action associated with the channel.
                media_pid (Optional[str]): Media process identifier.
                is_catchup_enabled (Optional[bool]): If catch-up is enabled for this channel.
                is_restricted (Optional[bool]): If there are restrictions on the channel.
                entitlements (Optional[dict]): A dictionary of entitlements for the channel.
                is_free_to_air (Optional[bool]): Whether the channel is free to air.
                is_audio (Optional[bool]): Whether the channel is audio only.
                dt_channel_number (Optional[int]): Digital terrestrial channel number.
                channel_id (Optional[str]): Unique identifier for the channel.
                quality (Optional[str]): Quality of the channel stream.
                distribution_types (Optional[List[str]]): Distribution types for the channel.
                distribution_urls (Optional[dict]): URLs for different distributions.
                is_iptv (bool): Whether the channel is IPTV.
                type (Optional[str]): Type of the channel.
                lowLatency (Optional[bool]): If the channel supports low latency.
                video_src_dash (Optional[str]): DASH video source URL.
                video_src_m3u (Optional[str]): M3U video source URL.
                pid_dash (Optional[str]): DASH process identifier.
                pid_m3u (Optional[str]): M3U process identifier.
                is_subscribed (Optional[bool]): Subscription status of the channel.
                description (Optional[str]): Description of the channel.
            """

            self.channel_number = channel_number
            self.station_id = station_id
            self.title = title
            self.is_adult = is_adult
            self.genres = genres or []
            self.channel_logo = channel_logo
            self.cta = cta
            self.media_pid = media_pid
            self.is_catchup_enabled = is_catchup_enabled
            self.is_restricted = is_restricted
            self.entitlements = entitlements or {}
            self.is_free_to_air = is_free_to_air
            self.is_audio = is_audio
            self.dt_channel_number = dt_channel_number
            self.channel_id = channel_id
            self.quality = quality
            self.distribution_types = distribution_types or []
            self.distribution_urls = distribution_urls or {}
            self.is_iptv = is_iptv
            self.type = type
            self.lowLatency = lowLatency
            self.video_src_dash = video_src_dash
            self.video_src_m3u = video_src_m3u
            self.pid_dash = pid_dash
            self.pid_m3u = pid_m3u
            self.is_subscribed = is_subscribed
            self.description = description

        def __repr__(self) -> str:
            """
            Return a string representation of the Channel instance, including all non-None attributes.

            Returns:
                str: A formatted string detailing the various attributes of the Channel object,
                    such as channel number, station ID, title, and other metadata including
                    genres, subscription status, and media sources.
            """

            statement = "Channel DETAILS: "
            if self.channel_number is not None:
                statement += f"Channel Number: {self.channel_number}\n"
            if self.station_id is not None:
                statement += f"Station ID: {self.station_id}\n"
            if self.title is not None:
                statement += f"Title: {self.title}\n"
            if self.is_adult is not None:
                statement += f"Is Adult: {self.is_adult}\n"
            if self.genres:
                statement += f"Genres: {self.genres}\n"
            if self.channel_logo is not None:
                statement += f"Channel Logo: {self.channel_logo}\n"
            if self.cta is not None:
                statement += f"CTA: {self.cta}\n"
            if self.media_pid is not None:
                statement += f"Media PID: {self.media_pid}\n"
            if self.is_catchup_enabled is not None:
                statement += f"Is Catchup Enabled: {self.is_catchup_enabled}\n"
            if self.is_restricted is not None:
                statement += f"Is Restricted: {self.is_restricted}\n"
            if self.entitlements:
                statement += f"Entitlements: {self.entitlements}\n"
            if self.is_free_to_air is not None:
                statement += f"Is Free To Air: {self.is_free_to_air}\n"
            if self.is_audio is not None:
                statement += f"Is Audio: {self.is_audio}\n"
            if self.dt_channel_number is not None:
                statement += f"DT Channel Number: {self.dt_channel_number}\n"
            if self.channel_id is not None:
                statement += f"Channel ID: {self.channel_id}\n"
            if self.quality is not None:
                statement += f"Quality: {self.quality}\n"
            if self.distribution_types:
                statement += f"Distribution Types: {self.distribution_types}\n"
            if self.distribution_urls:
                statement += f"Distribution URLs: {self.distribution_urls}\n"
            if self.is_iptv is not None:
                statement += f"Is IPTV: {self.is_iptv}\n"
            if self.type is not None:
                statement += f"Type: {self.type}\n"
            if self.lowLatency is not None:
                statement += f"Low Latency: {self.lowLatency}\n"
            if self.video_src_dash is not None:
                statement += f"Video Src Dash: {self.video_src_dash}\n"
            if self.video_src_m3u is not None:
                statement += f"Video Src M3U: {self.video_src_m3u}\n"
            if self.pid_dash is not None:
                statement += f"PID Dash: {self.pid_dash}\n"
            if self.pid_m3u is not None:
                statement += f"PID M3U: {self.pid_m3u}\n"
            if self.is_subscribed is not None:
                statement += f"Is Subscribed: {self.is_subscribed}\n"
            if self.description is not None:
                statement += f"Description: {self.description}\n"
            return statement

        def __eq__(self, other) -> bool:
            if not isinstance(other, APIQuery.Channel):
                return False
            return self.channel_number == other.channel_number

    class ProgramDesc:
        def __init__(
            self,
            min_length=None,
            max_length=None,
            channel_number=None,
            show_type=None,  # ("Movie","TVShow")
            is_adult=False,
            is_subscribed=True,
            is_audio=False,
            remaining_minutes=None,
            recording_available=None,
            catchup_enabled=None,
            exclude_channel_number=None,
            select_random=False,
            hasTimeshift=None,
            ratings=None,  # Single rating string or list of rating strings
            exclude_ratings=None,  # Single rating string or list of rating strings to exclude
            # Time range filtering
            min_remaining_minutes=None,  # Minimum remaining minutes
            max_remaining_minutes=None,  # Maximum remaining minutes
            select_alpha=False,
            require_episode_info=False,
        ):
            """
            Constructor for ProgramDesc.
            ProgramDesc is a class used to filter and sort results when retrieving program information.

            Args:
                min_length (int): Minimum length of the returned list.
                max_length (int): Maximum length of the returned list.
                channel_number (int): Filter by specific channel number.
                show_type (str): Filter by show type ("Movie","TVShow").
                is_adult (bool): Filter by adult programs.
                is_subscribed (bool): Filter by subscribed programs.
                is_audio (bool): Filter by audio programs.
                remaining_minutes (int): Filter by minimum remaining minutes (deprecated, use min_remaining_minutes).
                recording_available (bool): Filter by recording availability.
                catchup_enabled (bool): Filter by catchup availability.
                exclude_channel_number (int): Exclude a specific channel number.
                select_random (bool): Select programs randomly.
                hasTimeshift (bool): Filter by timeshift availability (default: False).
                ratings (Union[str, List[str]]): Single rating string or list of rating strings (e.g., "12" or ["12", "16"]).
                exclude_ratings (Union[str, List[str]]): Single rating string or list of rating strings to exclude.
                min_remaining_minutes (int): Minimum remaining minutes.
                max_remaining_minutes (int): Maximum remaining minutes.
                select_alpha (bool): Filter programs with alphabetic names only (default: False).
            """
            self.min_length = min_length
            self.max_length = max_length
            self.channel_number = channel_number
            self.show_type = show_type
            self.is_adult = is_adult
            self.is_subscribed = is_subscribed
            self.is_audio = is_audio

            # Handle remaining minutes (support both old and new parameter names)
            self.remaining_minutes = remaining_minutes or min_remaining_minutes
            self.min_remaining_minutes = min_remaining_minutes or remaining_minutes
            self.max_remaining_minutes = max_remaining_minutes
            self.recording_available = recording_available
            self.catchup_enabled = catchup_enabled
            self.exclude_channel_number = exclude_channel_number
            self.select_random = select_random
            self.hasTimeshift = hasTimeshift
            self.ratings = ratings
            self.exclude_ratings = exclude_ratings
            self.select_alpha = select_alpha  # NEW: Add select_alpha parameter
            self.require_episode_info = require_episode_info

        def matches_rating(self, program_rating):
            """
            Check if program rating matches the filtering criteria.

            Args:
                program_rating (str): The program's rating

            Returns:
                bool: True if rating matches criteria
            """
            # First check exclude_ratings - if program rating is in exclude list, reject it
            if self.exclude_ratings:
                # Handle single exclude rating string
                if isinstance(self.exclude_ratings, str):
                    if program_rating == self.exclude_ratings:
                        return False
                # Handle list of exclude ratings
                elif isinstance(self.exclude_ratings, list):
                    if program_rating in self.exclude_ratings:
                        return False

            # If no include ratings specified, and program passed exclude filter, accept it
            if not self.ratings:
                return True

            # Check include ratings
            # Handle single rating string
            if isinstance(self.ratings, str):
                return program_rating == self.ratings

            # Handle list of ratings
            if isinstance(self.ratings, list):
                return program_rating in self.ratings

            return True

        def matches_remaining_time(self, remaining_minutes_value):
            """
            Check if remaining time matches the filtering criteria.

            Args:
                remaining_minutes_value (float): Remaining minutes for the program

            Returns:
                bool: True if remaining time matches criteria
            """
            # Check minimum remaining minutes
            if self.min_remaining_minutes is not None:
                if remaining_minutes_value < self.min_remaining_minutes:
                    return False

            # Check maximum remaining minutes
            if self.max_remaining_minutes is not None:
                if remaining_minutes_value > self.max_remaining_minutes:
                    return False

            # Legacy support for remaining_minutes
            if (
                self.remaining_minutes is not None
                and self.min_remaining_minutes is None
            ):
                if remaining_minutes_value < self.remaining_minutes:
                    return False

            return True

        def __repr__(self) -> str:
            statement = "ProgramDesc DETAILS: \n"
            if self.min_length is not None:
                statement += f"Min Length: {self.min_length}\n"
            if self.max_length is not None:
                statement += f"Max Length: {self.max_length}\n"
            if self.channel_number is not None:
                statement += f"Channel Number: {self.channel_number}\n"
            if self.show_type is not None:
                statement += f"Show Type: {self.show_type}\n"
            if self.is_adult is not None:
                statement += f"Is Adult: {self.is_adult}\n"
            if self.is_subscribed is not None:
                statement += f"Is Subscribed: {self.is_subscribed}\n"
            if self.is_audio is not None:
                statement += f"Is Audio: {self.is_audio}\n"
            if self.min_remaining_minutes is not None:
                statement += f"Min Remaining Minutes: {self.min_remaining_minutes}\n"
            if self.max_remaining_minutes is not None:
                statement += f"Max Remaining Minutes: {self.max_remaining_minutes}\n"
            if self.remaining_minutes is not None:
                statement += (
                    f"Min Remaining Minutes (Legacy): {self.remaining_minutes}\n"
                )
            if self.recording_available is not None:
                statement += f"Recording Available: {self.recording_available}\n"
            if self.catchup_enabled is not None:
                statement += f"Catchup Enabled: {self.catchup_enabled}\n"
            if self.exclude_channel_number is not None:
                statement += f"Exclude Channel Number: {self.exclude_channel_number}\n"
            if self.select_random is not None:
                statement += f"Select Random: {self.select_random}\n"
            if self.hasTimeshift is not None:
                statement += f"Has Timeshift: {self.hasTimeshift}\n"
            if self.ratings is not None:
                statement += f"Ratings: {self.ratings}\n"
            if self.exclude_ratings is not None:
                statement += f"Exclude Ratings: {self.exclude_ratings}\n"
            if self.select_alpha is not None:
                statement += f"Select Alpha: {self.select_alpha}\n"
            if self.require_episode_info is not None:
                statement += f"Require Episode Info: {self.require_episode_info}\n"
            return statement

    class Program:
        def __init__(
            self,
            program_id=None,
            channel_number=None,
            channel=None,
            series_id=None,
            season_id=None,
            season_number=None,
            season_display_number=None,
            episode_name=None,
            episode_number=None,
            show_type=None,
            description=None,
            full_description=None,
            start_time=None,
            end_time=None,
            genres=None,
            release_year=None,
            cta=None,
            ratings=None,
            is_adult=False,
            image=None,
            is_recording_available_content=False,
            is_catchup_enabled=False,
            station_id=None,
            entitlements=None,
            media_id=None,
            listing_guid=None,
            glf_station_id=None,
            glf_program_id=None,
            catchup_id=None,
            catchup_key=None,
            is_blackout=None,
            slot_type=None,
            playback_restrictions=None,
            content_flags=None,
            warning_labels=None,
            runtime_seconds=None,
            metadata=None,
            poster_image_url=None,
            airing_type=None,
            has_sign_language=False,
            has_audio_description=False,
            has_closed_captions=False,
            hasTimeshift=False,  # NEW: Add hasTimeshift parameter,
            remaining_minutes=None,
        ):
            """
            Initialize a Program instance with various attributes related to program information.

            Args:
                program_id (str): Unique identifier for the program.
                channel_number (int): Channel number.
                channel (str): Channel name.
                series_id (str): Series identifier.
                season_id (str): Season identifier.
                season_number (int): Season number.
                season_display_number (str): Season display number.
                episode_name (str): Episode name.
                episode_number (int): Episode number.
                show_type (str): Show type ("TVShow", "Movie", etc.).
                description (str): Program description.
                full_description (str): Full program description.
                start_time (datetime): Start time of the program.
                end_time (datetime): End time of the program.
                genres (list): List of genres the program belongs to.
                release_year (int): Release year of the program.
                cta (str): Call to action associated with the program.
                ratings (dict): Ratings associated with the program.
                is_adult (bool): Whether the program is for adult content.
                image (str): URL or path to the program image.
                is_recording_available_content (bool): Whether recording is available for this program.
                is_catchup_enabled (bool): Whether catchup is enabled for this program.
                station_id (str): Station identifier.
                entitlements (dict): Entitlements associated with the program.
                media_id (str): Media identifier.
                listing_guid (str): GUID associated with the program listing.
                glf_station_id (str): GLF station identifier.
                glf_program_id (str): GLF program identifier.
                catchup_id (str): Catchup identifier.
                catchup_key (str): Catchup key.
                is_blackout (bool): Whether the program is blacked out.
                slot_type (str): Slot type.
                playback_restrictions (dict): Playback restrictions associated with the program.
                content_flags (dict): Content flags associated with the program.
                warning_labels (dict): Warning labels associated with the program.
                runtime_seconds (int): Runtime of the program in seconds.
                metadata (dict): Metadata associated with the program.
                poster_image_url (str): URL or path to the program poster image.
                airing_type (str): Airing type.
                has_sign_language (bool): Whether the program has sign language.
                has_audio_description (bool): Whether the program has audio description.
                has_closed_captions (bool): Whether the program has closed captions.
                hasTimeshift (bool): Whether the program has timeshift capability.
                hasRemainingMinutes (int): Remaining minutes for the program.
            """
            self.program_id = program_id
            self.channel_number = channel_number
            self.channel = channel
            self.series_id = series_id
            self.season_id = season_id
            self.season_number = season_number
            self.season_display_number = season_display_number
            self.episode_name = episode_name
            self.episode_number = episode_number
            self.show_type = show_type
            self.description = description
            self.full_description = full_description
            self.start_time = start_time
            self.end_time = end_time
            self.genres = genres or []
            self.release_year = release_year
            self.cta = cta
            self.ratings = ratings
            self.is_adult = is_adult
            self.image = image
            self.is_recording_available_content = is_recording_available_content
            self.is_catchup_enabled = is_catchup_enabled
            self.station_id = station_id
            self.entitlements = entitlements or {}
            self.media_id = media_id
            self.listing_guid = listing_guid
            self.glf_station_id = glf_station_id
            self.glf_program_id = glf_program_id
            self.catchup_id = catchup_id
            self.catchup_key = catchup_key
            self.is_blackout = is_blackout
            self.slot_type = slot_type
            self.playback_restrictions = playback_restrictions
            self.content_flags = content_flags
            self.warning_labels = warning_labels
            self.runtime_seconds = runtime_seconds
            self.metadata = metadata
            self.poster_image_url = poster_image_url
            self.airing_type = airing_type
            self.has_sign_language = has_sign_language
            self.has_audio_description = has_audio_description
            self.has_closed_captions = has_closed_captions
            self.hasTimeshift = hasTimeshift
            self.remaining_minutes = remaining_minutes

        def __repr__(self):
            """
            Return a string representation of the Program instance, including all non-None attributes.

            Returns:
                str: A formatted string detailing the various attributes of the Program object,
                    such as program ID, channel details, series and season information, episode details,
                    show type, descriptions, timings, genres, ratings, and other associated metadata.
            """
            statement = "Program DETAILS: \n"
            if self.program_id is not None:
                statement += f"Program ID: {self.program_id}\n"
            if self.channel_number is not None:
                statement += f"Channel Number: {self.channel_number}\n"
            if self.channel is not None:
                statement += f"Channel: {self.channel}\n"
            if self.series_id is not None:
                statement += f"Series ID: {self.series_id}\n"
            if self.season_id is not None:
                statement += f"Season ID: {self.season_id}\n"
            if self.season_number is not None:
                statement += f"Season Number: {self.season_number}\n"
            if self.season_display_number is not None:
                statement += f"Season Display Number: {self.season_display_number}\n"
            if self.episode_name is not None:
                statement += f"Episode Name: {self.episode_name}\n"
            if self.episode_number is not None:
                statement += f"Episode Number: {self.episode_number}\n"
            if self.show_type is not None:
                statement += f"Show Type: {self.show_type}\n"
            if self.description is not None:
                statement += f"Description: {self.description}\n"
            if self.full_description is not None:
                statement += f"Full Description: {self.full_description}\n"
            if self.start_time is not None:
                statement += f"Start Time: {self.start_time}\n"
            if self.end_time is not None:
                statement += f"End Time: {self.end_time}\n"
            if self.genres:
                statement += f"Genres: {self.genres}\n"
            if self.release_year is not None:
                statement += f"Release Year: {self.release_year}\n"
            if self.cta is not None:
                statement += f"CTA: {self.cta}\n"
            if self.ratings is not None:
                statement += f"Ratings: {self.ratings}\n"
            if self.is_adult is not None:
                statement += f"Is Adult: {self.is_adult}\n"
            if self.image is not None:
                statement += f"Image: {self.image}\n"
            if self.is_recording_available_content is not None:
                statement += (
                    f"Is Recording Available: {self.is_recording_available_content}\n"
                )
            if self.is_catchup_enabled is not None:
                statement += f"Is Catchup Enabled: {self.is_catchup_enabled}\n"
            if self.station_id is not None:
                statement += f"Station ID: {self.station_id}\n"
            if self.entitlements:
                statement += f"Entitlements: {self.entitlements}\n"
            if self.media_id is not None:
                statement += f"Media ID: {self.media_id}\n"
            if self.listing_guid is not None:
                statement += f"Listing GUID: {self.listing_guid}\n"
            if self.glf_station_id is not None:
                statement += f"GLF Station ID: {self.glf_station_id}\n"
            if self.glf_program_id is not None:
                statement += f"GLF Program ID: {self.glf_program_id}\n"
            if self.catchup_id is not None:
                statement += f"Catchup ID: {self.catchup_id}\n"
            if self.catchup_key is not None:
                statement += f"Catchup Key: {self.catchup_key}\n"
            if self.is_blackout is not None:
                statement += f"Is Blackout: {self.is_blackout}\n"
            if self.slot_type is not None:
                statement += f"Slot Type: {self.slot_type}\n"
            if self.playback_restrictions is not None:
                statement += f"Playback Restrictions: {self.playback_restrictions}\n"
            if self.content_flags is not None:
                statement += f"Content Flags: {self.content_flags}\n"
            if self.warning_labels is not None:
                statement += f"Warning Labels: {self.warning_labels}\n"
            if self.runtime_seconds is not None:
                statement += f"Runtime Seconds: {self.runtime_seconds}\n"
            if self.metadata is not None:
                statement += f"Metadata: {self.metadata}\n"
            if self.poster_image_url is not None:
                statement += f"Poster Image URL: {self.poster_image_url}\n"
            if self.airing_type is not None:
                statement += f"Airing Type: {self.airing_type}\n"
            if self.has_sign_language is not None:
                statement += f"Has Sign Language: {self.has_sign_language}\n"
            if self.has_audio_description is not None:
                statement += f"Has Audio Description: {self.has_audio_description}\n"
            if self.has_closed_captions is not None:
                statement += f"Has Closed Captions: {self.has_closed_captions}\n"
            if self.hasTimeshift is not None:
                statement += f"Has Timeshift: {self.hasTimeshift}\n"
            if self.remaining_minutes is not None:
                statement += f"Remaining Minutes: {self.remaining_minutes:.1f}\n"
            return statement

    class MovieDesc:
        def __init__(
            self,
            min_length=None,
            max_length=None,
            show_type=None,  # "Movie", "TVShow"
            is_adult=None,
            is_geo_blocked=None,
            is_device_not_compatible=None,
            has_trailer=None,
            has_rent_options=None,
            has_purchase_options=None,
            has_watch_options=None,
            has_catchup_schedules=None,
            has_channels=None,
            is_rentable_only=None,  # Movies that are ONLY available for rent (no free options)
            min_price=None,
            max_price=None,
            currency=None,
            quality=None,  # "HD", "SD", etc.
            has_sign_language=None,
            has_audio_description=None,
            has_closed_captions=None,
            content_type=None,  # "tvod", etc.
            rental_window_hours=None,  # Minimum rental window in hours
            episode_name=None,
            original_asset_id=None,
            exclude_asset_id=None,
            exclude_asset_ids=None,
            select_random=False,
            size=1,
            # Rail-specific filters
            rail_title=None,
            rail_index=None,
            select_alpha=False,
        ):
            """
            Constructor for MovieDesc.
            MovieDesc is a class used to filter and sort results when retrieving movie information.

            Args:
                min_length (int): Minimum length of the returned list.
                max_length (int): Maximum length of the returned list.
                show_type (str): Filter by show type ("Movie", "TVShow").
                is_adult (bool): Filter by adult content.
                is_geo_blocked (bool): Filter by geo-blocked content.
                is_device_not_compatible (bool): Filter by device compatibility.
                has_trailer (bool): Filter movies that have trailers.
                has_rent_options (bool): Filter movies with rental options.
                has_purchase_options (bool): Filter movies with purchase options.
                has_watch_options (bool): Filter movies with watch options.
                has_catchup_schedules (bool): Filter movies with catchup schedules.
                has_channels (bool): Filter movies available on channels.
                is_rentable_only (bool): Filter movies that are ONLY available for rent.
                min_price (float): Minimum rental/purchase price.
                max_price (float): Maximum rental/purchase price.
                currency (str): Currency filter ("EUR", "USD", etc.).
                quality (str): Quality filter ("HD", "SD", etc.).
                has_sign_language (bool): Filter by sign language availability.
                has_audio_description (bool): Filter by audio description availability.
                has_closed_captions (bool): Filter by closed captions availability.
                content_type (str): Content type filter ("tvod", etc.).
                rental_window_hours (int): Minimum rental window in hours.
                episode_name (str): Filter by specific episode name.
                original_asset_id (str): Filter by specific original asset ID.
                exclude_asset_id (str): Exclude specific asset ID.
                exclude_asset_ids (list): Exclude multiple asset IDs.
                select_random (bool): Select movies randomly.
                size (int): Number of movies to return.
                rail_title (str): Filter by specific rail title.
                rail_index (int): Filter by specific rail index.
            """
            self.min_length = min_length
            self.max_length = max_length
            self.show_type = show_type
            self.is_adult = is_adult
            self.is_geo_blocked = is_geo_blocked
            self.is_device_not_compatible = is_device_not_compatible
            self.has_trailer = has_trailer
            self.has_rent_options = has_rent_options
            self.has_purchase_options = has_purchase_options
            self.has_watch_options = has_watch_options
            self.has_catchup_schedules = has_catchup_schedules
            self.has_channels = has_channels
            self.is_rentable_only = is_rentable_only
            self.min_price = min_price
            self.max_price = max_price
            self.currency = currency
            self.quality = quality
            self.has_sign_language = has_sign_language
            self.has_audio_description = has_audio_description
            self.has_closed_captions = has_closed_captions
            self.content_type = content_type
            self.episode_name = episode_name
            self.original_asset_id = original_asset_id
            self.exclude_asset_id = exclude_asset_id
            self.exclude_asset_ids = exclude_asset_ids or []
            self.select_random = select_random
            self.size = size if size > 0 else 1
            # Rail-specific filters
            self.rail_title = rail_title
            self.rail_index = rail_index
            self.select_alpha = select_alpha  # NEW: Add select_alpha parameter

        def __repr__(self) -> str:
            statement = "MovieDesc DETAILS: \n"
            if self.min_length is not None:
                statement += f"Min Length: {self.min_length}\n"
            if self.max_length is not None:
                statement += f"Max Length: {self.max_length}\n"
            if self.show_type is not None:
                statement += f"Show Type: {self.show_type}\n"
            if self.is_adult is not None:
                statement += f"Is Adult: {self.is_adult}\n"
            if self.is_geo_blocked is not None:
                statement += f"Is Geo Blocked: {self.is_geo_blocked}\n"
            if self.is_device_not_compatible is not None:
                statement += (
                    f"Is Device Not Compatible: {self.is_device_not_compatible}\n"
                )
            if self.has_trailer is not None:
                statement += f"Has Trailer: {self.has_trailer}\n"
            if self.has_rent_options is not None:
                statement += f"Has Rent Options: {self.has_rent_options}\n"
            if self.has_purchase_options is not None:
                statement += f"Has Purchase Options: {self.has_purchase_options}\n"
            if self.has_watch_options is not None:
                statement += f"Has Watch Options: {self.has_watch_options}\n"
            if self.has_catchup_schedules is not None:
                statement += f"Has Catchup Schedules: {self.has_catchup_schedules}\n"
            if self.has_channels is not None:
                statement += f"Has Channels: {self.has_channels}\n"
            if self.is_rentable_only is not None:
                statement += f"Is Rentable Only: {self.is_rentable_only}\n"
            if self.min_price is not None:
                statement += f"Min Price: {self.min_price}\n"
            if self.max_price is not None:
                statement += f"Max Price: {self.max_price}\n"
            if self.currency is not None:
                statement += f"Currency: {self.currency}\n"
            if self.quality is not None:
                statement += f"Quality: {self.quality}\n"
            if self.has_sign_language is not None:
                statement += f"Has Sign Language: {self.has_sign_language}\n"
            if self.has_audio_description is not None:
                statement += f"Has Audio Description: {self.has_audio_description}\n"
            if self.has_closed_captions is not None:
                statement += f"Has Closed Captions: {self.has_closed_captions}\n"
            if self.content_type is not None:
                statement += f"Content Type: {self.content_type}\n"
            # if self.rental_window_hours is not None:
            #     statement += f"Rental Window Hours: {self.rental_window_hours}\n"
            if self.episode_name is not None:
                statement += f"Episode Name: {self.episode_name}\n"
            if self.original_asset_id is not None:
                statement += f"Original Asset ID: {self.original_asset_id}\n"
            if self.exclude_asset_id is not None:
                statement += f"Exclude Asset ID: {self.exclude_asset_id}\n"
            if self.exclude_asset_ids:
                statement += f"Exclude Asset IDs: {self.exclude_asset_ids}\n"
            if self.select_random is not None:
                statement += f"Select Random: {self.select_random}\n"
            statement += f"Size: {self.size}\n"
            if self.rail_title is not None:
                statement += f"Rail Title: {self.rail_title}\n"
            if self.rail_index is not None:
                statement += f"Rail Index: {self.rail_index}\n"
            if self.select_alpha is not None:
                statement += f"Select Alpha: {self.select_alpha}\n"
            return statement

    class Movie:
        def __init__(
            self,
            id=None,
            episode_name=None,
            original_asset_id=None,
            show_type=None,
            is_geo_blocked=None,
            is_device_not_compatible=None,
            blocked_channels=None,
            is_any_schedule_exist=None,
            provider_id=None,
            watch_options=None,
            subscribe_options=None,
            schedules=None,
            channels=None,
            catchup_schedules=None,
            channel_subscribe_options=None,
            trailer_options=None,
            rent_options=None,
            purchase_options=None,
            is_pinned=None,
            # Derived/computed fields
            has_trailer=None,
            has_rent_options=None,
            has_purchase_options=None,
            has_watch_options=None,
            has_catchup_schedules=None,
            has_channels=None,
            is_rentable_only=None,
            min_rent_price=None,
            max_rent_price=None,
            min_purchase_price=None,
            max_purchase_price=None,
            currencies=None,
            qualities=None,
            has_sign_language=None,
            has_audio_description=None,
            has_closed_captions=None,
            # Additional metadata
            title=None,
            description=None,
            thumbnail=None,
            poster_image_url=None,
            release_year=None,
            deeplink=None,
            cta_title=None,
            runtime_seconds=None,
            index=None,
            cast=0,
            crew=None,
            # Rail and positioning information
            rail_title=None,
            rail_index=None,
            position=None,  # Dictionary with rail and item position for navigation
        ):
            """
            Initialize a Movie instance with various attributes related to movie information.

            Args:
                id (str): Unique identifier for the movie.
                episode_name (str): Name of the episode/movie.
                original_asset_id (str): Original asset identifier.
                show_type (str): Type of show ("Movie", "TVShow", etc.).
                is_geo_blocked (bool): Whether the movie is geo-blocked.
                is_device_not_compatible (bool): Whether the movie is device compatible.
                blocked_channels (list): List of blocked channels.
                is_any_schedule_exist (bool): Whether any schedule exists.
                provider_id (str): Provider identifier.
                watch_options (list): Available watch options.
                subscribe_options (list): Available subscribe options.
                schedules (list): Available schedules.
                channels (dict): Available channels.
                catchup_schedules (list): Available catchup schedules.
                channel_subscribe_options (list): Channel subscribe options.
                trailer_options (list): Available trailer options.
                rent_options (list): Available rent options.
                purchase_options (list): Available purchase options.
                is_pinned (bool): Whether the movie is pinned.
                has_trailer (bool): Whether the movie has a trailer.
                has_rent_options (bool): Whether the movie has rent options.
                has_purchase_options (bool): Whether the movie has purchase options.
                has_watch_options (bool): Whether the movie has watch options.
                has_catchup_schedules (bool): Whether the movie has catchup schedules.
                has_channels (bool): Whether the movie has channels.
                is_rentable_only (bool): Whether the movie is only available for rent.
                min_rent_price (float): Minimum rental price.
                max_rent_price (float): Maximum rental price.
                min_purchase_price (float): Minimum purchase price.
                max_purchase_price (float): Maximum purchase price.
                currencies (list): Available currencies.
                qualities (list): Available qualities.
                has_sign_language (bool): Whether the movie has sign language.
                has_audio_description (bool): Whether the movie has audio description.
                has_closed_captions (bool): Whether the movie has closed captions.
                title (str): Title of the movie.
                description (str): Description of the movie.
                thumbnail (str): Thumbnail URL.
                poster_image_url (str): Poster image URL.
                release_year (int): Release year.
                deeplink (str): Deeplink URL.
                cta_title (str): Call-to-action title.
                runtime_seconds (int): Runtime in seconds.
                index (int): Index position within the rail.
                rail_title (str): Title of the rail this movie belongs to.
                rail_index (int): Index of the rail this movie belongs to.
                position (dict): Navigation position with rail and item indexes.
            """
            self.id = id
            self.episode_name = episode_name
            self.original_asset_id = original_asset_id
            self.show_type = show_type
            self.is_geo_blocked = is_geo_blocked
            self.is_device_not_compatible = is_device_not_compatible
            self.blocked_channels = blocked_channels or []
            self.is_any_schedule_exist = is_any_schedule_exist
            self.provider_id = provider_id

            # Action options
            self.watch_options = watch_options or []
            self.subscribe_options = subscribe_options or []
            self.schedules = schedules or []
            self.channels = channels or {}
            self.catchup_schedules = catchup_schedules or []
            self.channel_subscribe_options = channel_subscribe_options or []
            self.trailer_options = trailer_options or []
            self.rent_options = rent_options or []
            self.purchase_options = purchase_options or []
            self.is_pinned = is_pinned

            # Derived fields
            self.has_trailer = has_trailer
            self.has_rent_options = has_rent_options
            self.has_purchase_options = has_purchase_options
            self.has_watch_options = has_watch_options
            self.has_catchup_schedules = has_catchup_schedules
            self.has_channels = has_channels
            self.is_rentable_only = is_rentable_only
            self.min_rent_price = min_rent_price
            self.max_rent_price = max_rent_price
            self.min_purchase_price = min_purchase_price
            self.max_purchase_price = max_purchase_price
            self.currencies = currencies or []
            self.qualities = qualities or []
            self.has_sign_language = has_sign_language
            self.has_audio_description = has_audio_description
            self.has_closed_captions = has_closed_captions

            # Additional metadata
            self.title = title
            self.description = description
            self.thumbnail = thumbnail
            self.poster_image_url = poster_image_url
            self.release_year = release_year
            self.deeplink = deeplink
            self.cta_title = cta_title
            self.runtime_seconds = runtime_seconds
            self.index = index
            self.cast = cast
            self.crew = crew or []
            # Rail and positioning information
            self.rail_title = rail_title
            self.rail_index = rail_index
            self.position = position or {}

        def __repr__(self) -> str:
            """
            Return a string representation of the Movie instance, including all non-None attributes.

            Returns:
                str: A formatted string detailing the various attributes of the Movie object.
            """
            statement = "Movie DETAILS: \n"
            if self.id is not None:
                statement += f"ID: {self.id}\n"
            if self.episode_name is not None:
                statement += f"Episode Name: {self.episode_name}\n"
            if self.original_asset_id is not None:
                statement += f"Original Asset ID: {self.original_asset_id}\n"
            if self.show_type is not None:
                statement += f"Show Type: {self.show_type}\n"
            if self.is_geo_blocked is not None:
                statement += f"Is Geo Blocked: {self.is_geo_blocked}\n"
            if self.is_device_not_compatible is not None:
                statement += (
                    f"Is Device Not Compatible: {self.is_device_not_compatible}\n"
                )
            if self.blocked_channels:
                statement += f"Blocked Channels: {self.blocked_channels}\n"
            if self.is_any_schedule_exist is not None:
                statement += f"Is Any Schedule Exist: {self.is_any_schedule_exist}\n"
            if self.provider_id is not None:
                statement += f"Provider ID: {self.provider_id}\n"
            if self.has_trailer is not None:
                statement += f"Has Trailer: {self.has_trailer}\n"
            if self.has_rent_options is not None:
                statement += f"Has Rent Options: {self.has_rent_options}\n"
            if self.has_purchase_options is not None:
                statement += f"Has Purchase Options: {self.has_purchase_options}\n"
            if self.has_watch_options is not None:
                statement += f"Has Watch Options: {self.has_watch_options}\n"
            if self.has_catchup_schedules is not None:
                statement += f"Has Catchup Schedules: {self.has_catchup_schedules}\n"
            if self.has_channels is not None:
                statement += f"Has Channels: {self.has_channels}\n"
            if self.is_rentable_only is not None:
                statement += f"Is Rentable Only: {self.is_rentable_only}\n"
            if self.min_rent_price is not None:
                statement += f"Min Rent Price: {self.min_rent_price}\n"
            if self.max_rent_price is not None:
                statement += f"Max Rent Price: {self.max_rent_price}\n"
            if self.currencies:
                statement += f"Currencies: {self.currencies}\n"
            if self.qualities:
                statement += f"Qualities: {self.qualities}\n"
            if self.has_sign_language is not None:
                statement += f"Has Sign Language: {self.has_sign_language}\n"
            if self.has_audio_description is not None:
                statement += f"Has Audio Description: {self.has_audio_description}\n"
            if self.has_closed_captions is not None:
                statement += f"Has Closed Captions: {self.has_closed_captions}\n"
            if self.title is not None:
                statement += f"Title: {self.title}\n"
            if self.description is not None:
                statement += f"Description: {self.description}\n"
            if self.release_year is not None:
                statement += f"Release Year: {self.release_year}\n"
            if self.runtime_seconds is not None:
                statement += f"Runtime Seconds: {self.runtime_seconds}\n"
            if self.index is not None:
                statement += f"Index: {self.index}\n"
            if self.cast is not None:
                statement += f"Cast Count: {self.cast}\n"
            if self.crew is not None:
                statement += f"Crew : {self.crew}\n"
            if self.rail_title is not None:
                statement += f"Rail Title: {self.rail_title}\n"
            if self.rail_index is not None:
                statement += f"Rail Index: {self.rail_index}\n"
            if self.deeplink is not None:
                statement += f"Deeplink: {self.deeplink}\n"
            if self.position:
                statement += f"Position: {self.position}\n"
            return statement

        def __eq__(self, other) -> bool:
            if not isinstance(other, APIQuery.Movie):
                return False
            return self.id == other.id

    class AdultDesc:
        def __init__(
            self,
            min_length=None,
            max_length=None,
            show_type=None,  # "Movie", "TVShow", etc.
            is_geo_blocked=None,
            is_device_not_compatible=None,
            has_trailer=None,
            has_rent_options=None,
            has_purchase_options=None,
            has_watch_options=None,
            has_catchup_schedules=None,
            has_channels=None,
            has_schedules=None,
            is_restricted=None,
            channel_number=None,
            station_id=None,
            min_price=None,
            max_price=None,
            currency=None,
            quality=None,
            has_sign_language=None,
            has_audio_description=None,
            has_closed_captions=None,
            content_type=None,
            release_year=None,
            min_runtime_seconds=None,
            max_runtime_seconds=None,
            exclude_asset_id=None,
            exclude_asset_ids=None,
            select_random=False,
            size=10,
            rail_title=None,
            rail_index=None,
            select_alpha=False,
        ):
            """
            Constructor for AdultDesc.
            AdultDesc is a class used to filter and sort results when retrieving adult content information.

            Args:
                min_length (int): Minimum length of the description.
                max_length (int): Maximum length of the description.
                show_type (str): Filter by show type ("Movie", "TVShow").
                is_geo_blocked (bool): Filter by geo-blocked content.
                is_device_not_compatible (bool): Filter by device compatibility.
                has_trailer (bool): Filter content that has trailers.
                has_rent_options (bool): Filter content with rental options.
                has_purchase_options (bool): Filter content with purchase options.
                has_watch_options (bool): Filter content with watch options.
                has_catchup_schedules (bool): Filter content with catchup schedules.
                has_channels (bool): Filter content available on channels.
                has_schedules (bool): Filter content with schedules.
                is_restricted (bool): Filter by restricted content.
                channel_number (int): Filter by specific channel number.
                station_id (str): Filter by specific station ID.
                min_price (float): Minimum rental/purchase price.
                max_price (float): Maximum rental/purchase price.
                currency (str): Currency filter ("EUR", "USD", etc.).
                quality (str): Quality filter ("HD", "SD", etc.).
                has_sign_language (bool): Filter by sign language availability.
                has_audio_description (bool): Filter by audio description availability.
                has_closed_captions (bool): Filter by closed captions availability.
                content_type (str): Content type filter ("tvod", etc.).
                release_year (int): Filter by specific release year.
                min_runtime_seconds (int): Minimum runtime in seconds.
                max_runtime_seconds (int): Maximum runtime in seconds.
                exclude_asset_id (str): Exclude specific asset ID.
                exclude_asset_ids (list): Exclude multiple asset IDs.
                select_random (bool): Select content randomly.
                size (int): Number of items to return.
                rail_title (str): Filter by specific rail title.
                rail_index (int): Filter by specific rail index.
                select_alpha (bool): Filter content with alphabetic names only.
            """
            self.min_length = min_length
            self.max_length = max_length
            self.show_type = show_type
            self.is_geo_blocked = is_geo_blocked
            self.is_device_not_compatible = is_device_not_compatible
            self.has_trailer = has_trailer
            self.has_rent_options = has_rent_options
            self.has_purchase_options = has_purchase_options
            self.has_watch_options = has_watch_options
            self.has_catchup_schedules = has_catchup_schedules
            self.has_channels = has_channels
            self.has_schedules = has_schedules
            self.is_restricted = is_restricted
            self.channel_number = channel_number
            self.station_id = station_id
            self.min_price = min_price
            self.max_price = max_price
            self.currency = currency
            self.quality = quality
            self.has_sign_language = has_sign_language
            self.has_audio_description = has_audio_description
            self.has_closed_captions = has_closed_captions
            self.content_type = content_type
            self.release_year = release_year
            self.min_runtime_seconds = min_runtime_seconds
            self.max_runtime_seconds = max_runtime_seconds
            self.exclude_asset_id = exclude_asset_id
            self.exclude_asset_ids = exclude_asset_ids or []
            self.select_random = select_random
            self.size = size if size > 0 else 10
            self.rail_title = rail_title
            self.rail_index = rail_index
            self.select_alpha = select_alpha

        def __repr__(self) -> str:
            statement = "AdultDesc DETAILS: \n"
            if self.min_length is not None:
                statement += f"Min Length: {self.min_length}\n"
            if self.max_length is not None:
                statement += f"Max Length: {self.max_length}\n"
            if self.show_type is not None:
                statement += f"Show Type: {self.show_type}\n"
            if self.is_geo_blocked is not None:
                statement += f"Is Geo Blocked: {self.is_geo_blocked}\n"
            if self.is_device_not_compatible is not None:
                statement += (
                    f"Is Device Not Compatible: {self.is_device_not_compatible}\n"
                )
            if self.has_trailer is not None:
                statement += f"Has Trailer: {self.has_trailer}\n"
            if self.has_rent_options is not None:
                statement += f"Has Rent Options: {self.has_rent_options}\n"
            if self.has_purchase_options is not None:
                statement += f"Has Purchase Options: {self.has_purchase_options}\n"
            if self.has_watch_options is not None:
                statement += f"Has Watch Options: {self.has_watch_options}\n"
            if self.has_catchup_schedules is not None:
                statement += f"Has Catchup Schedules: {self.has_catchup_schedules}\n"
            if self.has_channels is not None:
                statement += f"Has Channels: {self.has_channels}\n"
            if self.has_schedules is not None:
                statement += f"Has Schedules: {self.has_schedules}\n"
            if self.is_restricted is not None:
                statement += f"Is Restricted: {self.is_restricted}\n"
            if self.channel_number is not None:
                statement += f"Channel Number: {self.channel_number}\n"
            if self.station_id is not None:
                statement += f"Station ID: {self.station_id}\n"
            if self.min_price is not None:
                statement += f"Min Price: {self.min_price}\n"
            if self.max_price is not None:
                statement += f"Max Price: {self.max_price}\n"
            if self.currency is not None:
                statement += f"Currency: {self.currency}\n"
            if self.quality is not None:
                statement += f"Quality: {self.quality}\n"
            if self.has_sign_language is not None:
                statement += f"Has Sign Language: {self.has_sign_language}\n"
            if self.has_audio_description is not None:
                statement += f"Has Audio Description: {self.has_audio_description}\n"
            if self.has_closed_captions is not None:
                statement += f"Has Closed Captions: {self.has_closed_captions}\n"
            if self.content_type is not None:
                statement += f"Content Type: {self.content_type}\n"
            if self.release_year is not None:
                statement += f"Release Year: {self.release_year}\n"
            if self.min_runtime_seconds is not None:
                statement += f"Min Runtime Seconds: {self.min_runtime_seconds}\n"
            if self.max_runtime_seconds is not None:
                statement += f"Max Runtime Seconds: {self.max_runtime_seconds}\n"
            if self.exclude_asset_id is not None:
                statement += f"Exclude Asset ID: {self.exclude_asset_id}\n"
            if self.exclude_asset_ids:
                statement += f"Exclude Asset IDs: {self.exclude_asset_ids}\n"
            if self.select_random is not None:
                statement += f"Select Random: {self.select_random}\n"
            statement += f"Size: {self.size}\n"
            if self.rail_title is not None:
                statement += f"Rail Title: {self.rail_title}\n"
            if self.rail_index is not None:
                statement += f"Rail Index: {self.rail_index}\n"
            if self.select_alpha is not None:
                statement += f"Select Alpha: {self.select_alpha}\n"
            return statement

    class Adult:
        def __init__(
            self,
            id=None,
            episode_name=None,
            original_asset_id=None,
            show_type=None,
            is_geo_blocked=None,
            is_device_not_compatible=None,
            blocked_channels=None,
            is_any_schedule_exist=None,
            provider_id=None,
            # Action options
            watch_options=None,
            subscribe_options=None,
            schedules=None,
            channels=None,
            catchup_schedules=None,
            channel_subscribe_options=None,
            trailer_options=None,
            rent_options=None,
            purchase_options=None,
            is_pinned=None,
            # Derived/computed fields
            has_trailer=None,
            has_rent_options=None,
            has_purchase_options=None,
            has_watch_options=None,
            has_catchup_schedules=None,
            has_channels=None,
            has_schedules=None,
            is_restricted=None,
            channel_number=None,
            station_id=None,
            min_rent_price=None,
            max_rent_price=None,
            min_purchase_price=None,
            max_purchase_price=None,
            currencies=None,
            qualities=None,
            has_sign_language=None,
            has_audio_description=None,
            has_closed_captions=None,
            content_type=None,
            runtime_seconds=None,
            release_year=None,
            # Additional metadata
            title=None,
            description=None,
            deeplink=None,
            # Rail and positioning information
            rail_title=None,
            rail_index=None,
            position=None,
        ):
            """
            Initialize an Adult content instance with various attributes.

            Args:
                id (str): Unique identifier for the adult content.
                episode_name (str): Name of the episode/content.
                original_asset_id (str): Original asset identifier.
                show_type (str): Type of show ("Movie", "TVShow", etc.).
                is_geo_blocked (bool): Whether the content is geo-blocked.
                is_device_not_compatible (bool): Whether the content is device compatible.
                blocked_channels (list): List of blocked channels.
                is_any_schedule_exist (bool): Whether any schedule exists.
                provider_id (str): Provider identifier.
                watch_options (list): Available watch options.
                subscribe_options (list): Available subscribe options.
                schedules (list): Available schedules.
                channels (dict): Available channels.
                catchup_schedules (list): Available catchup schedules.
                channel_subscribe_options (list): Channel subscribe options.
                trailer_options (list): Available trailer options.
                rent_options (list): Available rent options.
                purchase_options (list): Available purchase options.
                is_pinned (bool): Whether the content is pinned.
                has_trailer (bool): Whether the content has a trailer.
                has_rent_options (bool): Whether the content has rent options.
                has_purchase_options (bool): Whether the content has purchase options.
                has_watch_options (bool): Whether the content has watch options.
                has_catchup_schedules (bool): Whether the content has catchup schedules.
                has_channels (bool): Whether the content has channels.
                has_schedules (bool): Whether the content has schedules.
                is_restricted (bool): Whether the content is restricted.
                channel_number (int): Channel number.
                station_id (str): Station identifier.
                min_rent_price (float): Minimum rental price.
                max_rent_price (float): Maximum rental price.
                min_purchase_price (float): Minimum purchase price.
                max_purchase_price (float): Maximum purchase price.
                currencies (list): Available currencies.
                qualities (list): Available qualities.
                has_sign_language (bool): Whether the content has sign language.
                has_audio_description (bool): Whether the content has audio description.
                has_closed_captions (bool): Whether the content has closed captions.
                content_type (str): Content type.
                runtime_seconds (int): Runtime in seconds.
                release_year (int): Release year.
                title (str): Title of the content.
                description (str): Description of the content.
                rail_title (str): Title of the rail this content belongs to.
                rail_index (int): Index of the rail this content belongs to.
                position (dict): Navigation position with rail and item indexes.
            """
            self.id = id
            self.episode_name = episode_name
            self.original_asset_id = original_asset_id
            self.show_type = show_type
            self.is_geo_blocked = is_geo_blocked
            self.is_device_not_compatible = is_device_not_compatible
            self.blocked_channels = blocked_channels or []
            self.is_any_schedule_exist = is_any_schedule_exist
            self.provider_id = provider_id

            # Action options
            self.watch_options = watch_options or []
            self.subscribe_options = subscribe_options or []
            self.schedules = schedules or []
            self.channels = channels or {}
            self.catchup_schedules = catchup_schedules or []
            self.channel_subscribe_options = channel_subscribe_options or []
            self.trailer_options = trailer_options or []
            self.rent_options = rent_options or []
            self.purchase_options = purchase_options or []
            self.is_pinned = is_pinned

            # Derived fields
            self.has_trailer = has_trailer
            self.has_rent_options = has_rent_options
            self.has_purchase_options = has_purchase_options
            self.has_watch_options = has_watch_options
            self.has_catchup_schedules = has_catchup_schedules
            self.has_channels = has_channels
            self.has_schedules = has_schedules
            self.is_restricted = is_restricted
            self.channel_number = channel_number
            self.station_id = station_id
            self.min_rent_price = min_rent_price
            self.max_rent_price = max_rent_price
            self.min_purchase_price = min_purchase_price
            self.max_purchase_price = max_purchase_price
            self.currencies = currencies or []
            self.qualities = qualities or []
            self.has_sign_language = has_sign_language
            self.has_audio_description = has_audio_description
            self.has_closed_captions = has_closed_captions
            self.content_type = content_type
            self.runtime_seconds = runtime_seconds
            self.release_year = release_year

            # Additional metadata
            self.title = title
            self.description = description
            self.deeplink = deeplink

            # Rail and positioning information
            self.rail_title = rail_title
            self.rail_index = rail_index
            self.position = position or {}

        def __repr__(self) -> str:
            statement = "Adult DETAILS: \n"
            if self.id is not None:
                statement += f"ID: {self.id}\n"
            if self.episode_name is not None:
                statement += f"Episode Name: {self.episode_name}\n"
            if self.original_asset_id is not None:
                statement += f"Original Asset ID: {self.original_asset_id}\n"
            if self.show_type is not None:
                statement += f"Show Type: {self.show_type}\n"
            if self.is_geo_blocked is not None:
                statement += f"Is Geo Blocked: {self.is_geo_blocked}\n"
            if self.is_device_not_compatible is not None:
                statement += (
                    f"Is Device Not Compatible: {self.is_device_not_compatible}\n"
                )
            if self.blocked_channels:
                statement += f"Blocked Channels: {self.blocked_channels}\n"
            if self.is_any_schedule_exist is not None:
                statement += f"Is Any Schedule Exist: {self.is_any_schedule_exist}\n"
            if self.provider_id is not None:
                statement += f"Provider ID: {self.provider_id}\n"
            if self.has_trailer is not None:
                statement += f"Has Trailer: {self.has_trailer}\n"
            if self.has_rent_options is not None:
                statement += f"Has Rent Options: {self.has_rent_options}\n"
            if self.has_purchase_options is not None:
                statement += f"Has Purchase Options: {self.has_purchase_options}\n"
            if self.has_watch_options is not None:
                statement += f"Has Watch Options: {self.has_watch_options}\n"
            if self.has_catchup_schedules is not None:
                statement += f"Has Catchup Schedules: {self.has_catchup_schedules}\n"
            if self.has_channels is not None:
                statement += f"Has Channels: {self.has_channels}\n"
            if self.has_schedules is not None:
                statement += f"Has Schedules: {self.has_schedules}\n"
            if self.is_restricted is not None:
                statement += f"Is Restricted: {self.is_restricted}\n"
            if self.channel_number is not None:
                statement += f"Channel Number: {self.channel_number}\n"
            if self.station_id is not None:
                statement += f"Station ID: {self.station_id}\n"
            if self.min_rent_price is not None:
                statement += f"Min Rent Price: {self.min_rent_price}\n"
            if self.max_rent_price is not None:
                statement += f"Max Rent Price: {self.max_rent_price}\n"
            if self.currencies:
                statement += f"Currencies: {self.currencies}\n"
            if self.qualities:
                statement += f"Qualities: {self.qualities}\n"
            if self.has_sign_language is not None:
                statement += f"Has Sign Language: {self.has_sign_language}\n"
            if self.has_audio_description is not None:
                statement += f"Has Audio Description: {self.has_audio_description}\n"
            if self.has_closed_captions is not None:
                statement += f"Has Closed Captions: {self.has_closed_captions}\n"
            if self.content_type is not None:
                statement += f"Content Type: {self.content_type}\n"
            if self.runtime_seconds is not None:
                statement += f"Runtime Seconds: {self.runtime_seconds}\n"
            if self.release_year is not None:
                statement += f"Release Year: {self.release_year}\n"
            if self.title is not None:
                statement += f"Title: {self.title}\n"
            if self.description is not None:
                statement += f"Description: {self.description}\n"
            if self.rail_title is not None:
                statement += f"Rail Title: {self.rail_title}\n"
            if self.deeplink is not None:
                statement += f"Deeplink: {self.deeplink}\n"
            if self.rail_index is not None:
                statement += f"Rail Index: {self.rail_index}\n"
            if self.position:
                statement += f"Position: {self.position}\n"
            return statement

        def __eq__(self, other) -> bool:
            if not isinstance(other, APIQuery.Adult):
                return False
            return self.id == other.id

    class SeriesDesc:
        def __init__(
            self,
            min_length=None,
            max_length=None,
            show_type=None,  # "Movie", "TVShow", etc.
            is_geo_blocked=None,
            is_device_not_compatible=None,
            has_trailer=None,
            has_rent_options=None,
            has_purchase_options=None,
            has_watch_options=None,
            has_catchup_schedules=None,
            has_channels=None,
            has_schedules=None,
            is_restricted=None,
            channel_number=None,
            station_id=None,
            min_price=None,
            max_price=None,
            currency=None,
            quality=None,
            has_sign_language=None,
            has_audio_description=None,
            has_closed_captions=None,
            content_type=None,
            release_year=None,
            min_runtime_seconds=None,
            max_runtime_seconds=None,
            exclude_asset_id=None,
            exclude_asset_ids=None,
            select_random=False,
            size=100,
            rail_title=None,
            rail_index=None,
            select_alpha=False,
        ):
            """
            Constructor for AdultDesc.
            AdultDesc is a class used to filter and sort results when retrieving adult content information.

            Args:
                min_length (int): Minimum length of the description.
                max_length (int): Maximum length of the description.
                show_type (str): Filter by show type ("Movie", "TVShow").
                is_geo_blocked (bool): Filter by geo-blocked content.
                is_device_not_compatible (bool): Filter by device compatibility.
                has_trailer (bool): Filter content that has trailers.
                has_rent_options (bool): Filter content with rental options.
                has_purchase_options (bool): Filter content with purchase options.
                has_watch_options (bool): Filter content with watch options.
                has_catchup_schedules (bool): Filter content with catchup schedules.
                has_channels (bool): Filter content available on channels.
                has_schedules (bool): Filter content with schedules.
                is_restricted (bool): Filter by restricted content.
                channel_number (int): Filter by specific channel number.
                station_id (str): Filter by specific station ID.
                min_price (float): Minimum rental/purchase price.
                max_price (float): Maximum rental/purchase price.
                currency (str): Currency filter ("EUR", "USD", etc.).
                quality (str): Quality filter ("HD", "SD", etc.).
                has_sign_language (bool): Filter by sign language availability.
                has_audio_description (bool): Filter by audio description availability.
                has_closed_captions (bool): Filter by closed captions availability.
                content_type (str): Content type filter ("tvod", etc.).
                release_year (int): Filter by specific release year.
                min_runtime_seconds (int): Minimum runtime in seconds.
                max_runtime_seconds (int): Maximum runtime in seconds.
                exclude_asset_id (str): Exclude specific asset ID.
                exclude_asset_ids (list): Exclude multiple asset IDs.
                select_random (bool): Select content randomly.
                size (int): Number of items to return.
                rail_title (str): Filter by specific rail title.
                rail_index (int): Filter by specific rail index.
                select_alpha (bool): Filter content with alphabetic names only.
            """
            self.min_length = min_length
            self.max_length = max_length
            self.show_type = show_type
            self.is_geo_blocked = is_geo_blocked
            self.is_device_not_compatible = is_device_not_compatible
            self.has_trailer = has_trailer
            self.has_rent_options = has_rent_options
            self.has_purchase_options = has_purchase_options
            self.has_watch_options = has_watch_options
            self.has_catchup_schedules = has_catchup_schedules
            self.has_channels = has_channels
            self.has_schedules = has_schedules
            self.is_restricted = is_restricted
            self.channel_number = channel_number
            self.station_id = station_id
            self.min_price = min_price
            self.max_price = max_price
            self.currency = currency
            self.quality = quality
            self.has_sign_language = has_sign_language
            self.has_audio_description = has_audio_description
            self.has_closed_captions = has_closed_captions
            self.content_type = content_type
            self.release_year = release_year
            self.min_runtime_seconds = min_runtime_seconds
            self.max_runtime_seconds = max_runtime_seconds
            self.exclude_asset_id = exclude_asset_id
            self.exclude_asset_ids = exclude_asset_ids or []
            self.select_random = select_random
            self.size = size if size > 0 else 100
            self.rail_title = rail_title
            self.rail_index = rail_index
            self.select_alpha = select_alpha

        def __repr__(self) -> str:
            statement = "SeriesDesc DETAILS: \n"
            if self.min_length is not None:
                statement += f"Min Length: {self.min_length}\n"
            if self.max_length is not None:
                statement += f"Max Length: {self.max_length}\n"
            if self.show_type is not None:
                statement += f"Show Type: {self.show_type}\n"
            if self.is_geo_blocked is not None:
                statement += f"Is Geo Blocked: {self.is_geo_blocked}\n"
            if self.is_device_not_compatible is not None:
                statement += (
                    f"Is Device Not Compatible: {self.is_device_not_compatible}\n"
                )
            if self.has_trailer is not None:
                statement += f"Has Trailer: {self.has_trailer}\n"
            if self.has_rent_options is not None:
                statement += f"Has Rent Options: {self.has_rent_options}\n"
            if self.has_purchase_options is not None:
                statement += f"Has Purchase Options: {self.has_purchase_options}\n"
            if self.has_watch_options is not None:
                statement += f"Has Watch Options: {self.has_watch_options}\n"
            if self.has_catchup_schedules is not None:
                statement += f"Has Catchup Schedules: {self.has_catchup_schedules}\n"
            if self.has_channels is not None:
                statement += f"Has Channels: {self.has_channels}\n"
            if self.has_schedules is not None:
                statement += f"Has Schedules: {self.has_schedules}\n"
            if self.is_restricted is not None:
                statement += f"Is Restricted: {self.is_restricted}\n"
            if self.channel_number is not None:
                statement += f"Channel Number: {self.channel_number}\n"
            if self.station_id is not None:
                statement += f"Station ID: {self.station_id}\n"
            if self.min_price is not None:
                statement += f"Min Price: {self.min_price}\n"
            if self.max_price is not None:
                statement += f"Max Price: {self.max_price}\n"
            if self.currency is not None:
                statement += f"Currency: {self.currency}\n"
            if self.quality is not None:
                statement += f"Quality: {self.quality}\n"
            if self.has_sign_language is not None:
                statement += f"Has Sign Language: {self.has_sign_language}\n"
            if self.has_audio_description is not None:
                statement += f"Has Audio Description: {self.has_audio_description}\n"
            if self.has_closed_captions is not None:
                statement += f"Has Closed Captions: {self.has_closed_captions}\n"
            if self.content_type is not None:
                statement += f"Content Type: {self.content_type}\n"
            if self.release_year is not None:
                statement += f"Release Year: {self.release_year}\n"
            if self.min_runtime_seconds is not None:
                statement += f"Min Runtime Seconds: {self.min_runtime_seconds}\n"
            if self.max_runtime_seconds is not None:
                statement += f"Max Runtime Seconds: {self.max_runtime_seconds}\n"
            if self.exclude_asset_id is not None:
                statement += f"Exclude Asset ID: {self.exclude_asset_id}\n"
            if self.exclude_asset_ids:
                statement += f"Exclude Asset IDs: {self.exclude_asset_ids}\n"
            if self.select_random is not None:
                statement += f"Select Random: {self.select_random}\n"
            statement += f"Size: {self.size}\n"
            if self.rail_title is not None:
                statement += f"Rail Title: {self.rail_title}\n"
            if self.rail_index is not None:
                statement += f"Rail Index: {self.rail_index}\n"
            if self.select_alpha is not None:
                statement += f"Select Alpha: {self.select_alpha}\n"
            return statement

    class Series:
        def __init__(
            self,
            id=None,
            episode_name=None,
            original_asset_id=None,
            show_type=None,
            is_geo_blocked=None,
            is_device_not_compatible=None,
            blocked_channels=None,
            is_any_schedule_exist=None,
            provider_id=None,
            # Action options
            watch_options=None,
            subscribe_options=None,
            schedules=None,
            channels=None,
            catchup_schedules=None,
            channel_subscribe_options=None,
            trailer_options=None,
            rent_options=None,
            purchase_options=None,
            is_pinned=None,
            # Derived/computed fields
            has_trailer=None,
            has_rent_options=None,
            has_purchase_options=None,
            has_watch_options=None,
            has_catchup_schedules=None,
            has_channels=None,
            has_schedules=None,
            is_restricted=None,
            channel_number=None,
            station_id=None,
            min_rent_price=None,
            max_rent_price=None,
            min_purchase_price=None,
            max_purchase_price=None,
            currencies=None,
            qualities=None,
            has_sign_language=None,
            has_audio_description=None,
            has_closed_captions=None,
            content_type=None,
            runtime_seconds=None,
            release_year=None,
            # Additional metadata
            title=None,
            description=None,
            # Rail and positioning information
            rail_title=None,
            rail_index=None,
            position=None,
        ):
            """
            Initialize an Adult content instance with various attributes.

            Args:
                id (str): Unique identifier for the adult content.
                episode_name (str): Name of the episode/content.
                original_asset_id (str): Original asset identifier.
                show_type (str): Type of show ("Movie", "TVShow", etc.).
                is_geo_blocked (bool): Whether the content is geo-blocked.
                is_device_not_compatible (bool): Whether the content is device compatible.
                blocked_channels (list): List of blocked channels.
                is_any_schedule_exist (bool): Whether any schedule exists.
                provider_id (str): Provider identifier.
                watch_options (list): Available watch options.
                subscribe_options (list): Available subscribe options.
                schedules (list): Available schedules.
                channels (dict): Available channels.
                catchup_schedules (list): Available catchup schedules.
                channel_subscribe_options (list): Channel subscribe options.
                trailer_options (list): Available trailer options.
                rent_options (list): Available rent options.
                purchase_options (list): Available purchase options.
                is_pinned (bool): Whether the content is pinned.
                has_trailer (bool): Whether the content has a trailer.
                has_rent_options (bool): Whether the content has rent options.
                has_purchase_options (bool): Whether the content has purchase options.
                has_watch_options (bool): Whether the content has watch options.
                has_catchup_schedules (bool): Whether the content has catchup schedules.
                has_channels (bool): Whether the content has channels.
                has_schedules (bool): Whether the content has schedules.
                is_restricted (bool): Whether the content is restricted.
                channel_number (int): Channel number.
                station_id (str): Station identifier.
                min_rent_price (float): Minimum rental price.
                max_rent_price (float): Maximum rental price.
                min_purchase_price (float): Minimum purchase price.
                max_purchase_price (float): Maximum purchase price.
                currencies (list): Available currencies.
                qualities (list): Available qualities.
                has_sign_language (bool): Whether the content has sign language.
                has_audio_description (bool): Whether the content has audio description.
                has_closed_captions (bool): Whether the content has closed captions.
                content_type (str): Content type.
                runtime_seconds (int): Runtime in seconds.
                release_year (int): Release year.
                title (str): Title of the content.
                description (str): Description of the content.
                rail_title (str): Title of the rail this content belongs to.
                rail_index (int): Index of the rail this content belongs to.
                position (dict): Navigation position with rail and item indexes.
            """
            self.id = id
            self.episode_name = episode_name
            self.original_asset_id = original_asset_id
            self.show_type = show_type
            self.is_geo_blocked = is_geo_blocked
            self.is_device_not_compatible = is_device_not_compatible
            self.blocked_channels = blocked_channels or []
            self.is_any_schedule_exist = is_any_schedule_exist
            self.provider_id = provider_id

            # Action options
            self.watch_options = watch_options or []
            self.subscribe_options = subscribe_options or []
            self.schedules = schedules or []
            self.channels = channels or {}
            self.catchup_schedules = catchup_schedules or []
            self.channel_subscribe_options = channel_subscribe_options or []
            self.trailer_options = trailer_options or []
            self.rent_options = rent_options or []
            self.purchase_options = purchase_options or []
            self.is_pinned = is_pinned

            # Derived fields
            self.has_trailer = has_trailer
            self.has_rent_options = has_rent_options
            self.has_purchase_options = has_purchase_options
            self.has_watch_options = has_watch_options
            self.has_catchup_schedules = has_catchup_schedules
            self.has_channels = has_channels
            self.has_schedules = has_schedules
            self.is_restricted = is_restricted
            self.channel_number = channel_number
            self.station_id = station_id
            self.min_rent_price = min_rent_price
            self.max_rent_price = max_rent_price
            self.min_purchase_price = min_purchase_price
            self.max_purchase_price = max_purchase_price
            self.currencies = currencies or []
            self.qualities = qualities or []
            self.has_sign_language = has_sign_language
            self.has_audio_description = has_audio_description
            self.has_closed_captions = has_closed_captions
            self.content_type = content_type
            self.runtime_seconds = runtime_seconds
            self.release_year = release_year

            # Additional metadata
            self.title = title
            self.description = description

            # Rail and positioning information
            self.rail_title = rail_title
            self.rail_index = rail_index
            self.position = position or {}

        def __repr__(self) -> str:
            statement = "Adult DETAILS: \n"
            if self.id is not None:
                statement += f"ID: {self.id}\n"
            if self.episode_name is not None:
                statement += f"Episode Name: {self.episode_name}\n"
            if self.original_asset_id is not None:
                statement += f"Original Asset ID: {self.original_asset_id}\n"
            if self.show_type is not None:
                statement += f"Show Type: {self.show_type}\n"
            if self.is_geo_blocked is not None:
                statement += f"Is Geo Blocked: {self.is_geo_blocked}\n"
            if self.is_device_not_compatible is not None:
                statement += (
                    f"Is Device Not Compatible: {self.is_device_not_compatible}\n"
                )
            if self.blocked_channels:
                statement += f"Blocked Channels: {self.blocked_channels}\n"
            if self.is_any_schedule_exist is not None:
                statement += f"Is Any Schedule Exist: {self.is_any_schedule_exist}\n"
            if self.provider_id is not None:
                statement += f"Provider ID: {self.provider_id}\n"
            if self.has_trailer is not None:
                statement += f"Has Trailer: {self.has_trailer}\n"
            if self.has_rent_options is not None:
                statement += f"Has Rent Options: {self.has_rent_options}\n"
            if self.has_purchase_options is not None:
                statement += f"Has Purchase Options: {self.has_purchase_options}\n"
            if self.has_watch_options is not None:
                statement += f"Has Watch Options: {self.has_watch_options}\n"
            if self.has_catchup_schedules is not None:
                statement += f"Has Catchup Schedules: {self.has_catchup_schedules}\n"
            if self.has_channels is not None:
                statement += f"Has Channels: {self.has_channels}\n"
            if self.has_schedules is not None:
                statement += f"Has Schedules: {self.has_schedules}\n"
            if self.is_restricted is not None:
                statement += f"Is Restricted: {self.is_restricted}\n"
            if self.channel_number is not None:
                statement += f"Channel Number: {self.channel_number}\n"
            if self.station_id is not None:
                statement += f"Station ID: {self.station_id}\n"
            if self.min_rent_price is not None:
                statement += f"Min Rent Price: {self.min_rent_price}\n"
            if self.max_rent_price is not None:
                statement += f"Max Rent Price: {self.max_rent_price}\n"
            if self.currencies:
                statement += f"Currencies: {self.currencies}\n"
            if self.qualities:
                statement += f"Qualities: {self.qualities}\n"
            if self.has_sign_language is not None:
                statement += f"Has Sign Language: {self.has_sign_language}\n"
            if self.has_audio_description is not None:
                statement += f"Has Audio Description: {self.has_audio_description}\n"
            if self.has_closed_captions is not None:
                statement += f"Has Closed Captions: {self.has_closed_captions}\n"
            if self.content_type is not None:
                statement += f"Content Type: {self.content_type}\n"
            if self.runtime_seconds is not None:
                statement += f"Runtime Seconds: {self.runtime_seconds}\n"
            if self.release_year is not None:
                statement += f"Release Year: {self.release_year}\n"
            if self.title is not None:
                statement += f"Title: {self.title}\n"
            if self.description is not None:
                statement += f"Description: {self.description}\n"
            if self.rail_title is not None:
                statement += f"Rail Title: {self.rail_title}\n"
            if self.rail_index is not None:
                statement += f"Rail Index: {self.rail_index}\n"
            if self.position:
                statement += f"Position: {self.position}\n"
            return statement

        def __eq__(self, other) -> bool:
            if not isinstance(other, APIQuery.Adult):
                return False
            return self.id == other.id

    class RecordingsDesc:

        def __init__(
            self,
            type=None,
            item_state=None,
        ):
            self.type = type
            self.item_state = item_state

        def __repr__(self) -> str:
            statement = "RecordingsDesc DETAILS: \n"
            if self.type is not None:
                statement += f"Type: {self.type}\n"
            if self.item_state is not None:
                statement += f"Item State: {self.item_state}\n"
            return statement

    class Recordings:
        def __init__(
            self,
            id=None,
            type=None,
            title=None,
            item_state=None,
            is_recording_complete_series=None,
            series_detail=None,
            is_series=None,
            is_singleprogram=None,
            program_detail=None,
        ):

            self.id = id
            self.type = type
            self.title = title
            self.item_state = item_state
            self.is_recording_complete_series = is_recording_complete_series
            self.series_detail = series_detail
            self.is_series = is_series
            self.is_singleprogram = is_singleprogram
            self.program_detail = program_detail

        def __repr__(self) -> str:
            statement = "Recordings DETAILS: \n"
            if self.id is not None:
                statement += f"ID: {self.id}\n"
            if self.type is not None:
                statement += f"Type: {self.type}\n"
            if self.title is not None:
                statement += f"Title: {self.title}\n"
            if self.item_state is not None:
                statement += f"Item State: {self.item_state}\n"
            if self.is_series is not None:
                statement += f"Is Series: {self.is_series}\n"
            if self.is_singleprogram is not None:
                statement += f"Is SingleProgram: {self.is_singleprogram}\n"
            if self.is_recording_complete_series is not None:
                statement += f"Is Recording Complete Series: {self.is_recording_complete_series}\n"
            if self.series_detail is not None:
                statement += f"Series Detail: {self.series_detail}\n"
            if self.program_detail is not None:
                statement += f"Program Detail: {self.program_detail}\n"
            return statement

    class RentalContentDesc:
        def __init__(self, title=None, type=None, rating=None, quality=None):
            self.title = title
            self.type = type
            self.rating = rating
            self.quality = quality

        def __repr__(self) -> str:
            statement = "RentalcontentDesc DETAILS: \n"
            if self.title is not None:
                statement += f"Title: {self.title}\n"
            if self.type is not None:
                statement += f"Type: {self.type}\n"
            if self.rating is not None:
                statement += f"Rating: {self.rating}\n"
            if self.quality is not None:
                statement += f"Quality: {self.quality}\n"
            return statement

    class RentalContent:
        def __init__(
            self,
            id=None,
            type=None,
            title=None,
            rating=None,
            quality=None,
            deeplink=None,
        ):

            self.id = id
            self.type = type
            self.title = title
            self.rating = rating
            self.quality = quality
            self.deeplink = deeplink

        def __repr__(self) -> str:
            statement = "RentalContent DETAILS: \n"
            if self.id is not None:
                statement += f"ID: {self.id}\n"
            if self.type is not None:
                statement += f"Type: {self.type}\n"
            if self.title is not None:
                statement += f"Title: {self.title}\n"
            if self.rating is not None:
                statement += f"Rating: {self.rating}\n"
            if self.quality is not None:
                statement += f"Quality: {self.quality}\n"
            if self.deeplink is not None:
                statement += f"Deeplink: {self.deeplink}\n"
            return statement

    class WatchListDesc:
        def __init__(
            self,
            title=None,
            type=None,
            rating=None,
        ):
            self.title = title
            self.type = type
            self.rating = rating

        def __repr__(self) -> str:
            statement = "WatchListDesc DETAILS: \n"
            if self.title is not None:
                statement += f"Type: {self.title}\n"
            if self.type is not None:
                statement += f"Type: {self.type}\n"
            if self.rating is not None:
                statement += f"Rating: {self.rating}\n"
            return statement

    class WatchList:
        def __init__(
            self,
            id=None,
            type=None,
            title=None,
            rating=None,
        ):

            self.id = id
            self.type = type
            self.title = title
            self.rating = rating

        def __repr__(self) -> str:
            statement = "WatchList DETAILS: \n"
            if self.id is not None:
                statement += f"ID: {self.id}\n"
            if self.type is not None:
                statement += f"Type: {self.type}\n"
            if self.title is not None:
                statement += f"Title: {self.title}\n"
            if self.rating is not None:
                statement += f"Rating: {self.rating}\n"
            return statement

    class BookMarkDesc:
        def __init__(
            self,
            title=None,
            type=None,
        ):
            self.title = title
            self.type = type

        def __repr__(self) -> str:
            statement = "BookMarkDesc DETAILS: \n"
            if self.title is not None:
                statement += f"Title: {self.title}\n"
            if self.type is not None:
                statement += f"Type: {self.type}\n"
            return statement

    class BookMark:
        def __init__(
            self,
            id=None,
            type=None,
            title=None,
            deeplink=None,
        ):

            self.id = id
            self.type = type
            self.title = title
            self.deeplink = deeplink

        def __repr__(self) -> str:
            statement = "BookMark DETAILS: \n"
            if self.id is not None:
                statement += f"ID: {self.id}\n"
            if self.type is not None:
                statement += f"Type: {self.type}\n"
            if self.title is not None:
                statement += f"Title: {self.title}\n"
            if self.deeplink is not None:
                statement += f"Deeplink: {self.deeplink}\n"
            return statement


class Common:
    class Result:
        # @par Description:
        # Initialises Result with given parameter values
        # Default values would be set, when no details specified
        # @note
        #
        # @param result @b Boolean: It is up to the user to set the required value
        #         @e None - Default
        # @param data @b ANY: The data can be of any datatype as required by user
        # @return @b None
        #
        # @b Example:
        # @code
        #    return DataType.Common.Result(True, "Pass")
        # @endcode
        def __init__(self, result=None, data=None):
            self.result = result
            self.data = data

        # Function to handle str(Result)
        def __repr__(self):
            return "<Result: result:%s, data:%s>" % (self.result, str(self.data))

        # Function to handle if(result):
        def __nonzero__(self):
            return bool(self.result)

        # Provides the data type of stored result data
        def GetDataType(self):
            return self.data.__class__.__name__

        def Result(self):
            return self.result

        def Data(self):
            return self.data

