from __future__ import unicode_literals, absolute_import

import base64
import hashlib
import json

from .base_object import BaseObject
from ..pagination.limit_offset_based_dict_collection import LimitOffsetBasedDictCollection

class ChunkedUpload(object):
    _item_type = 'chunked_upload'
    _uploaded_part = None
    _part_array = []
    _sha1 = hashlib.sha1()

    def __init__(self, upload_session, content_stream, file_size):
        self._upload_session = upload_session
        self._content_stream = content_stream
        self._file_size = file_size

    def start(self):
        self._upload()
        content_sha1 = self._sha1.digest()
        self._upload_session.commit(content_sha1=content_sha1, parts=self._part_array)

    def _upload(self):
        while len(self._part_array) < self._upload_session.total_parts:
            chunk = self._read_chunk()
            self._uploaded_part = self._upload_session.upload_part_bytes(chunk, len(self._part_array)*self._upload_session.part_size,
                                                                         self._file_size)
            self._part_array.append(self._uploaded_part)
            self._sha1.update(chunk)

    def _read_chunk(self):
        copied_length = 0
        chunk = b''
        while copied_length < self._upload_session.part_size:
            bytes_read = self._content_stream.read(self._upload_session.part_size - copied_length)
            if bytes_read is None:
                # stream returns none when no bytes are ready currently but there are
                # potentially more bytes in the stream to be read.
                continue
            if len(bytes_read) == 0:
                # stream is exhausted.
                break
            chunk += bytes_read
            copied_length += len(bytes_read)
        return chunk
