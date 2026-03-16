export const SET_LOGIN_STATUS = "SET_LOGIN_STATUS";
export const SET_USERS_DATA = "SET_USERS_DATA";
export const SET_TRANSCRIPT = "SET_TRANSCRIPT";
export const SET_AUDIO_URL = "SET_AUDIO_URL";
export const SET_DID_DATA = "SET_DID_DATA";
export const SET_DID_LOADING = "SET_DID_LOADING";
export const SET_DID_ERROR = "SET_DID_ERROR";

export const setIsLoggedIn = (isLoggedIn) => ({
  type: SET_LOGIN_STATUS,
  payload: isLoggedIn,
});
export const setUsersData = (usersData) => ({
  type: SET_USERS_DATA,
  payload: usersData,
});
export const setTranscript = (transcript) => ({
  type: SET_TRANSCRIPT,
  payload: transcript,
});
export const setAudioUrl = (audioUrl) => ({
  type: SET_AUDIO_URL,
  payload: audioUrl,
});
export const setDIDData = (didData) => ({
  type: SET_DID_DATA,
  payload: didData,
});
export const setDIDLoading = (isLoading) => ({
  type: SET_DID_LOADING,
  payload: isLoading,
});
export const setDIDError = (error) => ({
  type: SET_DID_ERROR,
  payload: error,
});
