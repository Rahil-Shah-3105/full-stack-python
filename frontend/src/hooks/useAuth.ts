import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query"
import { useNavigate } from "@tanstack/react-router"

import {
  type Body_login_login_access_token as AccessToken,
  LoginService,
  type UserPublic,
  type UserRegister,
  UsersService,
} from "@/client"
import { handleError } from "@/utils"
import useCustomToast from "./useCustomToast"
const logger = console;

const isLoggedIn = () => {
logger.debug('>>> Entering isLoggedIn()');
logger.debug('<<< Exiting isLoggedIn()');
  return localStorage.getItem("access_token") !== null
}

const useAuth = () => {
logger.debug('>>> Entering useAuth()');
  const navigate = useNavigate()
  const queryClient = useQueryClient()
  const { showErrorToast } = useCustomToast()

logger.debug(`useAuth(): queryClient → ${queryClient}`);
  const { data: user } = useQuery<UserPublic | null, Error>({
    queryKey: ["currentUser"],
    queryFn: async () => (await UsersService.readUserMe()).data,
    enabled: isLoggedIn(),
  })

  const signUpMutation = useMutation({
    mutationFn: (data: UserRegister) =>
      UsersService.registerUser({ body: data }),
    onSuccess: () => {
      navigate({ to: "/login" })
    },
    onError: handleError.bind(showErrorToast),
    onSettled: () => {
      queryClient.invalidateQueries({ queryKey: ["users"] })
    },
  })

logger.debug(`useAuth(): signUpMutation.id → ${signUpMutation?.id}`);
  const login = async (data: AccessToken) => {
	logger.debug(`>>> Entering login(data=${data})`);
    const response = await LoginService.loginAccessToken({
      body: data,
    })
    localStorage.setItem("access_token", response.data.access_token)
	logger.debug(`login(data=${data}): response → ${response}`);
  }

  const loginMutation = useMutation({
    mutationFn: login,
    onSuccess: () => {
      navigate({ to: "/" })
    },
    onError: handleError.bind(showErrorToast),
  })

logger.debug(`useAuth(): loginMutation.id → ${loginMutation?.id}`);
  const logout = () => {
	logger.debug('>>> Entering logout()');
    localStorage.removeItem("access_token")
    navigate({ to: "/login" })
	logger.debug('<<< Exiting logout()');
  }

  return {
    signUpMutation,
    loginMutation,
    logout,
    user,
  }
logger.debug('<<< Exiting useAuth()');
}

export { isLoggedIn }
export default useAuth
