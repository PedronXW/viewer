from modules.receiver.domain.ports.repository.track import \
    TrackRepositoryAbstract
from modules.receiver.domain.ports.storage import StorageRepositoryAbstract
from modules.receiver.domain.track import Track, TrackProps


class CreateTrackService:
    def __init__(self, track_repository: TrackRepositoryAbstract):
        self.track_repository = track_repository

    async def execute(self, props: TrackProps) -> Track:
        track = Track(props)
        await self.track_repository.add(track)
        return track
        