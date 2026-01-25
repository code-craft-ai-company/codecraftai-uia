
from typing import Any, TYPE_CHECKING

import AppKit

from automojo.uia.platforms.macos.wrappers.wrappedobject import WrappedObject

if TYPE_CHECKING:
    from automojo.uia.platforms.macos.automation import MacOSAutomation

class UiaMetadataItem(WrappedObject):

    def __init__(self, controller: "MacOSAutomation", native_obj: Any):
        super().__init__(controller, native_obj)
        return
    
    @property
    def Audiences(self) -> str:
        rtnval = self.native_obj.valueForAttribute_(AppKit.NSMetadataItemAudiencesKey)
        return rtnval
    
    @property
    def AudioBitRate(self) -> str:
        rtnval = self.native_obj.valueForAttribute_(AppKit.NSMetadataItemAudioBitRateKey)
        return rtnval
    
    @property
    def AudioChannelCount(self) -> str:
        rtnval = self.native_obj.valueForAttribute_(AppKit.NSMetadataItemAudioChannelCountKey)
        return rtnval
    
    @property
    def AudioEncodingApplication(self) -> str:
        rtnval = self.native_obj.valueForAttribute_(AppKit.NSMetadataItemAudioEncodingApplicationKey)
        return rtnval
    
    @property
    def AudioSampleRate(self) -> str:
        rtnval = self.native_obj.valueForAttribute_(AppKit.NSMetadataItemAudioSampleRateKey)
        return rtnval
    
    @property
    def AudioTrackNumber(self) -> str:
        rtnval = self.native_obj.valueForAttribute_(AppKit.NSMetadataItemAudioTrackNumberKey)
        return rtnval
    
    @property
    def AuthorAddresses(self) -> str:
        rtnval = self.native_obj.valueForAttribute_(AppKit.NSMetadataItemAuthorAddressesKey)
        return rtnval
    
    @property
    def AuthorEmailAddresses(self) -> str:
        rtnval = self.native_obj.valueForAttribute_(AppKit.NSMetadataItemAuthorEmailAddressesKey)
        return rtnval
    
    @property
    def Authors(self) -> str:
        rtnval = self.native_obj.valueForAttribute_(AppKit.NSMetadataItemAuthorsKey)
        return rtnval
    
    @property
    def AcquisitionMake(self) -> str:
        rtnval = self.native_obj.valueForAttribute_(AppKit.NSMetadataItemAcquisitionMakeKey)
        return rtnval

    @property
    def AcquisitionModel(self) -> str:
        rtnval = self.native_obj.valueForAttribute_(AppKit.NSMetadataItemAcquisitionModelKey)
        return rtnval
    
    @property
    def Album(self) -> str:
        rtnval = self.native_obj.valueForAttribute_(AppKit.NSMetadataItemAlbumKey)
        return rtnval
    
    @property
    def Altitude(self) -> str:
        rtnval = self.native_obj.valueForAttribute_(AppKit.NSMetadataItemAltitudeKey)
        return rtnval
    
    @property
    def Aperture(self) -> str:
        rtnval = self.native_obj.valueForAttribute_(AppKit.NSMetadataItemApertureKey)
        return rtnval
    
    @property
    def AppleLoopDescriptors(self) -> str:
        rtnval = self.native_obj.valueForAttribute_(AppKit.NSMetadataItemAppleLoopDescriptorsKey)
        return rtnval
    
    @property
    def AppleLoopsKeyFilterType(self) -> str:
        rtnval = self.native_obj.valueForAttribute_(AppKit.NSMetadataItemAppleLoopsKeyFilterTypeKey)
        return rtnval
    
    @property
    def AppleLoopsLoopMode(self) -> str:
        rtnval = self.native_obj.valueForAttribute_(AppKit.NSMetadataItemAppleLoopsLoopModeKey)
        return rtnval
    
    @property
    def AppleLoopsRootKey(self) -> str:
        rtnval = self.native_obj.valueForAttribute_(AppKit.NSMetadataItemAppleLoopsRootKeyKey)
        return rtnval
    
    @property
    def ApplicationCategories(self) -> str:
        rtnval = self.native_obj.valueForAttribute_(AppKit.NSMetadataItemApplicationCategoriesKey)
        return rtnval
    
    @property
    def AttributeChangeDate(self) -> str:
        rtnval = self.native_obj.valueForAttribute_(AppKit.NSMetadataItemAttributeChangeDateKey)
        return rtnval
    
    @property
    def BitsPerSample(self) -> str:
        rtnval = self.native_obj.valueForAttribute_(AppKit.NSMetadataItemBitsPerSampleKey)
        return rtnval
    
    @property
    def CameraOwner(self) -> str:
        rtnval = self.native_obj.valueForAttribute_(AppKit.NSMetadataItemCameraOwnerKey)
        return rtnval
    
    @property
    def CFBundleIdentifier(self) -> str:
        rtnval = self.native_obj.valueForAttribute_(AppKit.NSMetadataItemCFBundleIdentifierKey)
        return rtnval
    
    @property
    def City(self) -> str:
        rtnval = self.native_obj.valueForAttribute_(AppKit.NSMetadataItemCityKey)
        return rtnval
    
    @property
    def Codecs(self) -> str:
        rtnval = self.native_obj.valueForAttribute_(AppKit.NSMetadataItemCodecsKey)
        return rtnval
    
    @property
    def ColorSpace(self) -> str:
        rtnval = self.native_obj.valueForAttribute_(AppKit.NSMetadataItemColorSpaceKey)
        return rtnval
    
    @property
    def Comment(self) -> str:
        rtnval = self.native_obj.valueForAttribute_(AppKit.NSMetadataItemCommentKey)
        return rtnval
    
    @property
    def Composer(self) -> str:
        rtnval = self.native_obj.valueForAttribute_(AppKit.NSMetadataItemComposerKey)
        return rtnval

    @property
    def ContactKeywords(self) -> str:
        rtnval = self.native_obj.valueForAttribute_(AppKit.NSMetadataItemContactKeywordsKey)
        return rtnval
    
    @property
    def ContentCreationDate(self) -> str:
        rtnval = self.native_obj.valueForAttribute_(AppKit.NSMetadataItemContentCreationDateKey)
        return rtnval
    
    @property
    def ContentModificationDate(self) -> str:
        rtnval = self.native_obj.valueForAttribute_(AppKit.NSMetadataItemContentModificationDateKey)
        return rtnval
    
    @property
    def ContentType(self) -> str:
        rtnval = self.native_obj.valueForAttribute_(AppKit.NSMetadataItemContentTypeKey)
        return rtnval
    
    @property
    def ContentTypeTree(self) -> str:
        rtnval = self.native_obj.valueForAttribute_(AppKit.NSMetadataItemContentTypeTreeKey)
        return rtnval
    
    @property
    def Contributors(self) -> str:
        rtnval = self.native_obj.valueForAttribute_(AppKit.NSMetadataItemContributorsKey)
        return rtnval
    
    @property
    def Copyright(self) -> str:
        rtnval = self.native_obj.valueForAttribute_(AppKit.NSMetadataItemCopyrightKey)
        return rtnval
    
    @property
    def Country(self) -> str:
        rtnval = self.native_obj.valueForAttribute_(AppKit.NSMetadataItemCountryKey)
        return rtnval

    @property
    def Coverage(self) -> str:
        rtnval = self.native_obj.valueForAttribute_(AppKit.NSMetadataItemCoverageKey)
        return rtnval

    @property
    def Creator(self) -> str:
        rtnval = self.native_obj.valueForAttribute_(AppKit.NSMetadataItemCreatorKey)
        return rtnval

    @property
    def DateAdded(self) -> str:
        rtnval = self.native_obj.valueForAttribute_(AppKit.NSMetadataItemDateAddedKey)
        return rtnval
    
    @property
    def DeliveryType(self) -> str:
        rtnval = self.native_obj.valueForAttribute_(AppKit.NSMetadataItemDeliveryTypeKey)
        return rtnval

    @property
    def Description(self) -> str:
        rtnval = self.native_obj.valueForAttribute_(AppKit.NSMetadataItemDescriptionKey)
        return rtnval
    
    @property
    def Director(self) -> str:
        rtnval = self.native_obj.valueForAttribute_(AppKit.NSMetadataItemDirectorKey)
        return rtnval
    
    @property
    def DisplayName(self) -> str:
        rtnval = self.native_obj.valueForAttribute_(AppKit.NSMetadataItemDisplayNameKey)
        return rtnval

    @property
    def DownloadedDate(self) -> str:
        rtnval = self.native_obj.valueForAttribute_(AppKit.NSMetadataItemDownloadedDateKey)
        return rtnval

    @property
    def DueDate(self) -> str:
        rtnval = self.native_obj.valueForAttribute_(AppKit.NSMetadataItemDueDateKey)
        return rtnval

    @property
    def DurationSeconds(self) -> str:
        rtnval = self.native_obj.valueForAttribute_(AppKit.NSMetadataItemDurationSecondsKey)
        return rtnval

    @property
    def Editors(self) -> str:
        rtnval = self.native_obj.valueForAttribute_(AppKit.NSMetadataItemEditorsKey)
        return rtnval

    @property
    def EmailAddresses(self) -> str:
        rtnval = self.native_obj.valueForAttribute_(AppKit.NSMetadataItemEmailAddressesKey)
        return rtnval
    
    @property
    def EncodingApplications(self) -> str:
        rtnval = self.native_obj.valueForAttribute_(AppKit.NSMetadataItemEncodingApplicationsKey)
        return rtnval
    
    @property
    def ExecutableArchitectures(self) -> str:
        rtnval = self.native_obj.valueForAttribute_(AppKit.NSMetadataItemExecutableArchitecturesKey)
        return rtnval

    @property
    def ExecutablePlatform(self) -> str:
        rtnval = self.native_obj.valueForAttribute_(AppKit.NSMetadataItemExecutablePlatformKey)
        return rtnval

    @property
    def EXIFGPSVersion(self) -> str:
        rtnval = self.native_obj.valueForAttribute_(AppKit.NSMetadataItemEXIFGPSVersionKey)
        return rtnval

    @property
    def EXIFVersion(self) -> str:
        rtnval = self.native_obj.valueForAttribute_(AppKit.NSMetadataItemEXIFVersionKey)
        return rtnval

    @property
    def ExposureMode(self) -> str:
        rtnval = self.native_obj.valueForAttribute_(AppKit.NSMetadataItemExposureModeKey)
        return rtnval

    @property
    def ExposureProgram(self) -> str:
        rtnval = self.native_obj.valueForAttribute_(AppKit.NSMetadataItemExposureProgramKey)
        return rtnval

    @property
    def ExposureTimeSeconds(self) -> str:
        rtnval = self.native_obj.valueForAttribute_(AppKit.NSMetadataItemExposureTimeSecondsKey)
        return rtnval
    
    @property
    def ExposureTimeString(self) -> str:
        rtnval = self.native_obj.valueForAttribute_(AppKit.NSMetadataItemExposureTimeStringKey)
        return rtnval

    @property
    def FSCreationDate(self) -> str:
        rtnval = self.native_obj.valueForAttribute_(AppKit.NSMetadataItemFSCreationDateKey)
        return rtnval
    
    @property
    def FSContentChangeDate(self) -> str:
        rtnval = self.native_obj.valueForAttribute_(AppKit.NSMetadataItemFSContentChangeDateKey)
        return rtnval

    @property
    def FSName(self) -> str:
        rtnval = self.native_obj.valueForAttribute_(AppKit.NSMetadataItemFSNameKey)
        return rtnval
    
    @property
    def FSSize(self) -> str:
        rtnval = self.native_obj.valueForAttribute_(AppKit.NSMetadataItemFSSizeKey)
        return rtnval

    @property
    def FNumber(self) -> str:
        rtnval = self.native_obj.valueForAttribute_(AppKit.NSMetadataItemFNumberKey)
        return rtnval
    
    @property
    def FinderComment(self) -> str:
        rtnval = self.native_obj.valueForAttribute_(AppKit.NSMetadataItemFinderCommentKey)
        return rtnval

    @property
    def FlashOnOff(self) -> str:
        rtnval = self.native_obj.valueForAttribute_(AppKit.NSMetadataItemFlashOnOffKey)
        return rtnval

    @property
    def FocalLength35mm(self) -> str:
        rtnval = self.native_obj.valueForAttribute_(AppKit.NSMetadataItemFocalLength35mmKey)
        return rtnval

    @property
    def FocalLength(self) -> str:
        rtnval = self.native_obj.valueForAttribute_(AppKit.NSMetadataItemFocalLengthKey)
        return rtnval
    
    @property
    def Fonts(self) -> str:
        rtnval = self.native_obj.valueForAttribute_(AppKit.NSMetadataItemFontsKey)
        return rtnval
    
    @property
    def GPSAreaInformation(self) -> str:
        rtnval = self.native_obj.valueForAttribute_(AppKit.NSMetadataItemGPSAreaInformationKey)
        return rtnval
    
    @property
    def GPSDOP(self) -> str:
        rtnval = self.native_obj.valueForAttribute_(AppKit.NSMetadataItemGPSDOPKey)
        return rtnval

    @property
    def GPSDateStamp(self) -> str:
        rtnval = self.native_obj.valueForAttribute_(AppKit.NSMetadataItemGPSDateStampKey)
        return rtnval
    
    @property
    def GPSDestBearing(self) -> str:
        rtnval = self.native_obj.valueForAttribute_(AppKit.NSMetadataItemGPSDestBearingKey)
        return rtnval

    @property
    def GPSDestDistance(self) -> str:
        rtnval = self.native_obj.valueForAttribute_(AppKit.NSMetadataItemGPSDestDistanceKey)
        return rtnval

    @property
    def GPSDestLatitude(self) -> str:
        rtnval = self.native_obj.valueForAttribute_(AppKit.NSMetadataItemGPSDestLatitudeKey)
        return rtnval

    @property
    def GPSDestLongitude(self) -> str:
        rtnval = self.native_obj.valueForAttribute_(AppKit.NSMetadataItemGPSDestLongitudeKey)
        return rtnval

    @property
    def GPSDifferental(self) -> str:
        rtnval = self.native_obj.valueForAttribute_(AppKit.NSMetadataItemGPSDifferentalKey)
        return rtnval

    @property
    def GPSMapDatum(self) -> str:
        rtnval = self.native_obj.valueForAttribute_(AppKit.NSMetadataItemGPSMapDatumKey)
        return rtnval

    @property
    def GPSMeasureMode(self) -> str:
        rtnval = self.native_obj.valueForAttribute_(AppKit.NSMetadataItemGPSMeasureModeKey)
        return rtnval

    @property
    def GPSProcessingMethod(self) -> str:
        rtnval = self.native_obj.valueForAttribute_(AppKit.NSMetadataItemGPSProcessingMethodKey)
        return rtnval

    @property
    def GPSStatus(self) -> str:
        rtnval = self.native_obj.valueForAttribute_(AppKit.NSMetadataItemGPSStatusKey)
        return rtnval

    @property
    def GPSTrack(self) -> str:
        rtnval = self.native_obj.valueForAttribute_(AppKit.NSMetadataItemGPSTrackKey)
        return rtnval

    @property
    def Genre(self) -> str:
        rtnval = self.native_obj.valueForAttribute_(AppKit.NSMetadataItemGenreKey)
        return rtnval

    @property
    def HasAlphaChannel(self) -> str:
        rtnval = self.native_obj.valueForAttribute_(AppKit.NSMetadataItemHasAlphaChannelKey)
        return rtnval

    @property
    def Headline(self) -> str:
        rtnval = self.native_obj.valueForAttribute_(AppKit.NSMetadataItemHeadlineKey)
        return rtnval

    @property
    def ISOSpeed(self) -> str:
        rtnval = self.native_obj.valueForAttribute_(AppKit.NSMetadataItemISOSpeedKey)
        return rtnval

    @property
    def Identifier(self) -> str:
        rtnval = self.native_obj.valueForAttribute_(AppKit.NSMetadataItemIdentifierKey)
        return rtnval
    
    @property
    def ImageDirection(self) -> str:
        rtnval = self.native_obj.valueForAttribute_(AppKit.NSMetadataItemImageDirectionKey)
        return rtnval

    @property
    def Information(self) -> str:
        rtnval = self.native_obj.valueForAttribute_(AppKit.NSMetadataItemInformationKey)
        return rtnval

    @property
    def InstantMessageAddresses(self) -> str:
        rtnval = self.native_obj.valueForAttribute_(AppKit.NSMetadataItemInstantMessageAddressesKey)
        return rtnval

    @property
    def Instructions(self) -> str:
        rtnval = self.native_obj.valueForAttribute_(AppKit.NSMetadataItemInstructionsKey)
        return rtnval

    @property
    def IsApplicationManaged(self) -> str:
        rtnval = self.native_obj.valueForAttribute_(AppKit.NSMetadataItemIsApplicationManagedKey)
        return rtnval

    @property
    def IsGeneralMIDISequence(self) -> str:
        rtnval = self.native_obj.valueForAttribute_(AppKit.NSMetadataItemIsGeneralMIDISequenceKey)
        return rtnval

    @property
    def IsLikelyJunk(self) -> str:
        rtnval = self.native_obj.valueForAttribute_(AppKit.NSMetadataItemIsLikelyJunkKey)
        return rtnval
    
    @property
    def KeySignature(self) -> str:
        rtnval = self.native_obj.valueForAttribute_(AppKit.NSMetadataItemKeySignatureKey)
        return rtnval
    
    @property
    def Keywords(self) -> str:
        rtnval = self.native_obj.valueForAttribute_(AppKit.NSMetadataItemKeywordsKey)
        return rtnval
    
    @property
    def Kind(self) -> str:
        rtnval = self.native_obj.valueForAttribute_(AppKit.NSMetadataItemKindKey)
        return rtnval

    @property
    def Languages(self) -> str:
        rtnval = self.native_obj.valueForAttribute_(AppKit.NSMetadataItemLanguagesKey)
        return rtnval

    @property
    def LastUsedDate(self) -> str:
        rtnval = self.native_obj.valueForAttribute_(AppKit.NSMetadataItemLastUsedDateKey)
        return rtnval

    @property
    def Latitude(self) -> str:
        rtnval = self.native_obj.valueForAttribute_(AppKit.NSMetadataItemLatitudeKey)
        return rtnval

    @property
    def LayerNames(self) -> str:
        rtnval = self.native_obj.valueForAttribute_(AppKit.NSMetadataItemLayerNamesKey)
        return rtnval

    @property
    def LensModel(self) -> str:
        rtnval = self.native_obj.valueForAttribute_(AppKit.NSMetadataItemLensModelKey)
        return rtnval

    @property
    def Longitude(self) -> str:
        rtnval = self.native_obj.valueForAttribute_(AppKit.NSMetadataItemLongitudeKey)
        return rtnval

    @property
    def Lyricist(self) -> str:
        rtnval = self.native_obj.valueForAttribute_(AppKit.NSMetadataItemLyricistKey)
        return rtnval

    @property
    def MaxAperture(self) -> str:
        rtnval = self.native_obj.valueForAttribute_(AppKit.NSMetadataItemMaxApertureKey)
        return rtnval

    @property
    def MediaTypes(self) -> str:
        rtnval = self.native_obj.valueForAttribute_(AppKit.NSMetadataItemMediaTypesKey)
        return rtnval

    @property
    def MeteringMode(self) -> str:
        rtnval = self.native_obj.valueForAttribute_(AppKit.NSMetadataItemMeteringModeKey)
        return rtnval

    @property
    def MusicalGenre(self) -> str:
        rtnval = self.native_obj.valueForAttribute_(AppKit.NSMetadataItemMusicalGenreKey)
        return rtnval

    @property
    def MusicalInstrumentCategory(self) -> str:
        rtnval = self.native_obj.valueForAttribute_(AppKit.NSMetadataItemMusicalInstrumentCategoryKey)
        return rtnval

    @property
    def MusicalInstrumentName(self) -> str:
        rtnval = self.native_obj.valueForAttribute_(AppKit.NSMetadataItemMusicalInstrumentNameKey)
        return rtnval

    @property
    def NamedLocation(self) -> str:
        rtnval = self.native_obj.valueForAttribute_(AppKit.NSMetadataItemNamedLocationKey)
        return rtnval
    
    @property
    def NumberOfPages(self) -> str:
        rtnval = self.native_obj.valueForAttribute_(AppKit.NSMetadataItemNumberOfPagesKey)
        return rtnval

    @property
    def Organizations(self) -> str:
        rtnval = self.native_obj.valueForAttribute_(AppKit.NSMetadataItemOrganizationsKey)
        return rtnval

    @property
    def Orientation(self) -> str:
        rtnval = self.native_obj.valueForAttribute_(AppKit.NSMetadataItemOrientationKey)
        return rtnval
    
    @property
    def OriginalFormat(self) -> str:
        rtnval = self.native_obj.valueForAttribute_(AppKit.NSMetadataItemOriginalFormatKey)
        return rtnval
    
    @property
    def OriginalSource(self) -> str:
        rtnval = self.native_obj.valueForAttribute_(AppKit.NSMetadataItemOriginalSourceKey)
        return rtnval

    @property
    def PageHeight(self) -> str:
        rtnval = self.native_obj.valueForAttribute_(AppKit.NSMetadataItemPageHeightKey)
        return rtnval

    @property
    def PageWidth(self) -> str:
        rtnval = self.native_obj.valueForAttribute_(AppKit.NSMetadataItemPageWidthKey)
        return rtnval

    @property
    def Participants(self) -> str:
        rtnval = self.native_obj.valueForAttribute_(AppKit.NSMetadataItemParticipantsKey)
        return rtnval

    @property
    def Path(self) -> str:
        rtnval = self.native_obj.valueForAttribute_(AppKit.NSMetadataItemPathKey)
        return rtnval

    @property
    def Performers(self) -> str:
        rtnval = self.native_obj.valueForAttribute_(AppKit.NSMetadataItemPerformersKey)
        return rtnval
    
    @property
    def PhoneNumbers(self) -> str:
        rtnval = self.native_obj.valueForAttribute_(AppKit.NSMetadataItemPhoneNumbersKey)
        return rtnval
    
    @property
    def PixelCount(self) -> str:
        rtnval = self.native_obj.valueForAttribute_(AppKit.NSMetadataItemPixelCountKey)
        return rtnval
    
    @property
    def PixelHeight(self) -> str:
        rtnval = self.native_obj.valueForAttribute_(AppKit.NSMetadataItemPixelHeightKey)
        return rtnval
    
    @property
    def PixelWidth(self) -> str:
        rtnval = self.native_obj.valueForAttribute_(AppKit.NSMetadataItemPixelWidthKey)
        return rtnval
    
    @property
    def Producer(self) -> str:
        rtnval = self.native_obj.valueForAttribute_(AppKit.NSMetadataItemProducerKey)
        return rtnval

    @property
    def ProfileName(self) -> str:
        rtnval = self.native_obj.valueForAttribute_(AppKit.NSMetadataItemProfileNameKey)
        return rtnval
    
    @property
    def Projects(self) -> str:
        rtnval = self.native_obj.valueForAttribute_(AppKit.NSMetadataItemProjectsKey)
        return rtnval

    @property
    def Publishers(self) -> str:
        rtnval = self.native_obj.valueForAttribute_(AppKit.NSMetadataItemPublishersKey)
        return rtnval
    
    @property
    def RecipientAddresses(self) -> str:
        rtnval = self.native_obj.valueForAttribute_(AppKit.NSMetadataItemRecipientAddressesKey)
        return rtnval
    
    @property
    def RecipientEmailAddresses(self) -> str:
        rtnval = self.native_obj.valueForAttribute_(AppKit.NSMetadataItemRecipientEmailAddressesKey)
        return rtnval
    
    @property
    def Recipients(self) -> str:
        rtnval = self.native_obj.valueForAttribute_(AppKit.NSMetadataItemRecipientsKey)
        return rtnval
    
    @property
    def RecordingDate(self) -> str:
        rtnval = self.native_obj.valueForAttribute_(AppKit.NSMetadataItemRecordingDateKey)
        return rtnval
    
    @property
    def RecordingYear(self) -> str:
        rtnval = self.native_obj.valueForAttribute_(AppKit.NSMetadataItemRecordingYearKey)
        return rtnval
    
    @property
    def RedEyeOnOff(self) -> str:
        rtnval = self.native_obj.valueForAttribute_(AppKit.NSMetadataItemRedEyeOnOffKey)
        return rtnval

    @property
    def ResolutionHeightDPI(self) -> str:
        rtnval = self.native_obj.valueForAttribute_(AppKit.NSMetadataItemResolutionHeightDPIKey)
        return rtnval

    @property
    def ResolutionWidthDPI(self) -> str:
        rtnval = self.native_obj.valueForAttribute_(AppKit.NSMetadataItemResolutionWidthDPIKey)
        return rtnval

    @property
    def Rights(self) -> str:
        rtnval = self.native_obj.valueForAttribute_(AppKit.NSMetadataItemRightsKey)
        return rtnval
    
    @property
    def SecurityMethod(self) -> str:
        rtnval = self.native_obj.valueForAttribute_(AppKit.NSMetadataItemSecurityMethodKey)
        return rtnval
    
    @property
    def Speed(self) -> str:
        rtnval = self.native_obj.valueForAttribute_(AppKit.NSMetadataItemSpeedKey)
        return rtnval

    @property
    def StarRating(self) -> str:
        rtnval = self.native_obj.valueForAttribute_(AppKit.NSMetadataItemStarRatingKey)
        return rtnval
    
    @property
    def StateOrProvince(self) -> str:
        rtnval = self.native_obj.valueForAttribute_(AppKit.NSMetadataItemStateOrProvinceKey)
        return rtnval
    
    @property
    def Streamable(self) -> str:
        rtnval = self.native_obj.valueForAttribute_(AppKit.NSMetadataItemStreamableKey)
        return rtnval
    
    @property
    def Subject(self) -> str:
        rtnval = self.native_obj.valueForAttribute_(AppKit.NSMetadataItemSubjectKey)
        return rtnval
    
    @property
    def Tempo(self) -> str:
        rtnval = self.native_obj.valueForAttribute_(AppKit.NSMetadataItemTempoKey)
        return rtnval
    
    @property
    def TextContent(self) -> str:
        rtnval = self.native_obj.valueForAttribute_(AppKit.NSMetadataItemTextContentKey)
        return rtnval

    @property
    def Theme(self) -> str:
        rtnval = self.native_obj.valueForAttribute_(AppKit.NSMetadataItemThemeKey)
        return rtnval
    
    @property
    def TimeSignature(self) -> str:
        rtnval = self.native_obj.valueForAttribute_(AppKit.NSMetadataItemTimeSignatureKey)
        return rtnval
    
    @property
    def Timestamp(self) -> str:
        rtnval = self.native_obj.valueForAttribute_(AppKit.NSMetadataItemTimestampKey)
        return rtnval
    
    @property
    def Title(self) -> str:
        rtnval = self.native_obj.valueForAttribute_(AppKit.NSMetadataItemTitleKey)
        return rtnval
    
    @property
    def TotalBitRate(self) -> str:
        rtnval = self.native_obj.valueForAttribute_(AppKit.NSMetadataItemTotalBitRateKey)
        return rtnval
    
    @property
    def Version(self) -> str:
        rtnval = self.native_obj.valueForAttribute_(AppKit.NSMetadataItemVersionKey)
        return rtnval
    
    @property
    def VideoBitRate(self) -> str:
        rtnval = self.native_obj.valueForAttribute_(AppKit.NSMetadataItemVideoBitRateKey)
        return rtnval
    
    @property
    def WhereFroms(self) -> str:
        rtnval = self.native_obj.valueForAttribute_(AppKit.NSMetadataItemWhereFromsKey)
        return rtnval
    
    @property
    def WhiteBalance(self) -> str:
        rtnval = self.native_obj.valueForAttribute_(AppKit.NSMetadataItemWhiteBalanceKey)
        return rtnval
    
    @property
    def URL(self) -> str:
        rtnval = self.native_obj.valueForAttribute_(AppKit.NSMetadataItemURLKey)
        return rtnval

