/*
 * This program is free software; you can redistribute it and/or
 * modify it under the terms of the GNU General Public License
 * as published by the Free Software Foundation; either version 2
 * of the License, or (at your option) any later version.
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with this program; if not, write to the Free Software Foundation,
 * Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
 */

/** \file
 * \ingroup blenloader
 */
#include "BLO_readfile.h"

#include "MEM_guardedalloc.h"

#include "BLI_string.h"

#include "BKE_main.h"
#include "BKE_report.h"

#include "DNA_ID.h"

TempLibraryContext *BLO_library_temp_load_id(struct Main *real_main,
                                             const char *blend_file_path,
                                             const short idcode,
                                             const char *idname,
                                             struct ReportList *reports)
{
  TempLibraryContext *temp_lib_ctx = MEM_callocN(sizeof(*temp_lib_ctx), __func__);
  temp_lib_ctx->bmain_base = BKE_main_new();

  /* Copy the file path so any path remapping is performed properly. */
  STRNCPY(temp_lib_ctx->bmain_base->name, real_main->name);

  temp_lib_ctx->blendhandle = BLO_blendhandle_from_file(blend_file_path, reports);

  BLO_library_link_params_init(
      &temp_lib_ctx->liblink_params, temp_lib_ctx->bmain_base, 0, LIB_TAG_TEMP_MAIN);

  temp_lib_ctx->bmain_lib = BLO_library_link_begin(
      &temp_lib_ctx->blendhandle, blend_file_path, &temp_lib_ctx->liblink_params);

  temp_lib_ctx->temp_id = BLO_library_link_named_part(temp_lib_ctx->bmain_lib,
                                                      &temp_lib_ctx->blendhandle,
                                                      idcode,
                                                      idname,
                                                      &temp_lib_ctx->liblink_params);

  return temp_lib_ctx;
}

void BLO_library_temp_free(TempLibraryContext *temp_lib_ctx)
{
  /* This moves the temporary ID and any indirectly loaded data into `bmain_base`
   * only to free `bmain_base`, while redundant this is the typical code-path for library linking,
   * it's more convenient to follow this convention rather than create a new code-path for this
   * one-off use case. */
  BLO_library_link_end(
      temp_lib_ctx->bmain_lib, &temp_lib_ctx->blendhandle, &temp_lib_ctx->liblink_params);
  BLO_blendhandle_close(temp_lib_ctx->blendhandle);
  BKE_main_free(temp_lib_ctx->bmain_base);
  MEM_freeN(temp_lib_ctx);
}