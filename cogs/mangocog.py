from __main__ import settings, botdata, loggingdb_session
from cogs.utils.helpers import *
from cogs.utils.clip import *
from cogs.utils.loggingdb import convert_message



class MangoCog:
	def __init__(self, bot):
		self.bot = bot
		self.emoji_dict = read_json(settings.resource("json/emoji.json"))

	def get_emoji(self, key):
		return self.emoji_dict.get(key, f":{key}:")

	async def log_message(self, message):
		msg = convert_message(message)
		loggingdb_session.add(msg)
		loggingdb_session.commit()
		print(msg)

	async def get_clip_try_types(self, clipid, trytypes=""):
		trytypes = trytypes.split("|")
		try:
			return await self.get_clip(clipid)
		except MissingClipType:
			while len(trytypes) > 0:
				try:
					return await self.get_clip("{}:{}".format(trytypes.pop(), clipid))
				except ClipNotFound:
					continue
		raise MissingClipType(clipid)

	async def get_clip(self, clipid):
		cliptypes = Clip.types_dict()

		match = re.search(f"^({'|'.join(cliptypes)}):(.*)$", clipid.replace("\n", " "))

		if not match:
			raise MissingClipType(clipid)

		return cliptypes[match.group(1)](match.group(2), self.bot)


	async def play_clip(self, clip, ctx):
		if isinstance(clip, str):
			clip = await self.get_clip(clip)

		audio = self.bot.get_cog("Audio")
		await (await audio.audioplayer(ctx)).queue_clip(clip)