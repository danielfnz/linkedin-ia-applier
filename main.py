import time
import math
import random
import os
import utils
import constants
import config
import pickle
import hashlib

from selenium import webdriver
from selenium.webdriver.common.by import By

from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.support.ui import Select
import openai
from openai import OpenAI
from docling.document_converter import DocumentConverter

if not os.path.exists("cv.md"):
    utils.prGreen("Convert to .md")
    source = config.cvName
    converter = DocumentConverter()
    result = converter.convert(source)
    with open("cv.md", "w", encoding="utf-8") as f:
        f.write(result.document.export_to_markdown())
        f.write("\n- Meu LinkedIn ProfileURL - "+config.LinkedInProfileURL)
        f.write("\n- Minha localização - "+config.Location)
        f.write("\n- Expectativa salarial CLT - "+config.salaryCLT)
        f.write("\n- Expectativa salarial PJ - "+config.salaryPJ)

client = OpenAI(
    # This is the default and can be omitted
    api_key=config.apikeyOpenAI,
)

# Cria um vector store (banco vetorial)
vector_store = client.vector_stores.create(name="LinkedIn AI Apply Bot")

# Envia o PDF para dentro do vector store
file = client.files.create(
    file=open("cv.md", "rb"),
    purpose="assistants"
)

client.vector_stores.files.create(
    vector_store_id=vector_store.id,
    file_id=file.id
)


class Linkedin:
    def __init__(self):
        utils.prYellow(
            "🌐 Bot will run in Chrome browser and log in Linkedin for you.")
        self.driver = webdriver.Chrome(service=ChromeService(
            ChromeDriverManager().install()), options=utils.chromeBrowserOptions())
        self.cookies_path = f"{os.path.join(os.getcwd(), 'cookies')}/{self.getHash(config.email)}.pkl"
        self.driver.get('https://www.linkedin.com')
        self.loadCookies()

        if not self.isLoggedIn():
            self.driver.get(
                "https://www.linkedin.com/login?trk=guest_homepage-basic_nav-header-signin")
            utils.prYellow("🔄 Trying to log in Linkedin...")
            try:
                self.driver.find_element(
                    "id", "username").send_keys(config.email)
                time.sleep(2)
                self.driver.find_element(
                    "id", "password").send_keys(config.password)
                time.sleep(2)
                self.driver.find_element(
                    "xpath", '//button[@type="submit"]').click()
                time.sleep(30)
            except:
                utils.prRed(
                    "❌ Couldn't log in Linkedin by using Chrome. Please check your Linkedin credentials on config files line 7 and 8.")

            self.saveCookies()
        # start application
        self.linkJobApply()

    def getHash(self, string):
        return hashlib.md5(string.encode('utf-8')).hexdigest()

    def loadCookies(self):
        if os.path.exists(self.cookies_path):
            cookies = pickle.load(open(self.cookies_path, "rb"))
            self.driver.delete_all_cookies()
            for cookie in cookies:
                self.driver.add_cookie(cookie)

    def saveCookies(self):
        pickle.dump(self.driver.get_cookies(), open(self.cookies_path, "wb"))

    def isLoggedIn(self):
        self.driver.get('https://www.linkedin.com/feed')
        try:
            self.driver.find_element(By.XPATH, '//*[@id="ember14"]')
            return True
        except:
            pass
        return False

    def generateUrls(self):
        if not os.path.exists('data'):
            os.makedirs('data')
        try:
            with open('data/urlData.txt', 'w', encoding="utf-8") as file:
                linkedinJobLinks = utils.LinkedinUrlGenerate().generateUrlLinks()
                for url in linkedinJobLinks:
                    file.write(url + "\n")
            utils.prGreen(
                "✅ Apply urls are created successfully, now the bot will visit those urls.")
        except:
            utils.prRed(
                "❌ Couldn't generate urls, make sure you have editted config file line 25-39")

    def linkJobApply(self):
        self.generateUrls()
        countApplied = 0
        countJobs = 0

        urlData = utils.getUrlDataFile()

        for url in urlData:
            self.driver.get(url)
            time.sleep(random.uniform(1, constants.botSpeed))

            totalJobs = self.driver.find_element(By.XPATH, '//small').text
            totalPages = utils.jobsToPages(totalJobs)

            urlWords = utils.urlToKeywords(url)
            lineToWrite = "\n Category: " + \
                urlWords[0] + ", Location: " + urlWords[1] + \
                ", Applying " + str(totalJobs) + " jobs."
            self.displayWriteResults(lineToWrite)

            for page in range(totalPages):
                currentPageJobs = constants.jobsPerPage * page
                url = url + "&start=" + str(currentPageJobs)
                self.driver.get(url)
                time.sleep(random.uniform(1, constants.botSpeed))

                offersPerPage = self.driver.find_elements(
                    By.XPATH, '//li[@data-occludable-job-id]')
                offerIds = [(offer.get_attribute(
                    "data-occludable-job-id").split(":")[-1]) for offer in offersPerPage]
                time.sleep(random.uniform(1, constants.botSpeed))

                for offer in offersPerPage:
                    if not self.element_exists(offer, By.XPATH, ".//li[contains(@class, 'job-card-container__footer-job-state') and normalize-space(text())='Applied']"):
                        offerId = offer.get_attribute("data-occludable-job-id")
                        offerIds.append(int(offerId.split(":")[-1]))

                for jobID in offerIds:
                    offerPage = 'https://www.linkedin.com/jobs/view/' + \
                        str(jobID)
                    self.driver.get(offerPage)
                    time.sleep(random.uniform(1, constants.botSpeed))

                    countJobs += 1

                    jobProperties = self.getJobProperties(countJobs)
                    if "blacklisted" in jobProperties:
                        lineToWrite = jobProperties + " | " + \
                            "* 🤬 Blacklisted Job, skipped!: " + str(offerPage)
                        self.displayWriteResults(lineToWrite)

                    else:
                        easyApplybutton = self.easyApplyButton()

                        if easyApplybutton is not False:
                            applyPage = 'https://www.linkedin.com/jobs/view/' + \
                                str(jobID) + '/apply'
                            self.driver.get(applyPage)

                            time.sleep(random.uniform(
                                1, constants.botSpeed))

                            try:
                                self.chooseResume()

                                self.driver.find_element(
                                    By.CSS_SELECTOR, "button[aria-label='Submit application']").click()
                                time.sleep(random.uniform(
                                    1, constants.botSpeed))

                                lineToWrite = jobProperties + " | " + \
                                    "* 🥳 Just Applied to this job: " + \
                                    str(offerPage)
                                self.displayWriteResults(lineToWrite)
                                countApplied += 1

                            except:
                                try:
                                    self.driver.find_element(
                                        By.CSS_SELECTOR, "button[aria-label='Continue to next step']").click()
                                    time.sleep(random.uniform(
                                        1, constants.botSpeed))

                                    self.chooseResume()

                                    comPercentage = self.driver.find_element(
                                        By.XPATH, '//progress[contains(@class, "progress")]').get_attribute("value")
                                    percenNumber = int(comPercentage)

                                    result = self.applyProcess(
                                        percenNumber, offerPage)
                                    lineToWrite = jobProperties + " | " + result
                                    self.displayWriteResults(lineToWrite)

                                except Exception:
                                    self.chooseResume()
                                    lineToWrite = jobProperties + " | " + \
                                        "* 🥵 Cannot apply to this Job! " + \
                                        str(offerPage)
                                    self.displayWriteResults(lineToWrite)
                        else:
                            lineToWrite = jobProperties + " | " + \
                                "* 🥳 Already applied! Job: " + str(offerPage)
                            self.displayWriteResults(lineToWrite)

            utils.prYellow("Category: " + urlWords[0] + "," + urlWords[1] + " applied: " + str(countApplied) +
                           " jobs out of " + str(countJobs) + ".")

        utils.donate(self)

    def chooseResume(self):
        try:
            self.driver.find_element(
                By.CLASS_NAME, "jobs-document-upload__title--is-required")
            resumes = self.driver.find_elements(
                By.XPATH, "//div[contains(@class, 'ui-attachment--pdf')]")
            if (len(resumes) == 1 and resumes[0].get_attribute("aria-label") == "Select this resume"):
                resumes[0].click()
            elif (len(resumes) > 1 and resumes[config.preferredCv-1].get_attribute("aria-label") == "Select this resume"):
                resumes[config.preferredCv-1].click()
            elif (type(len(resumes)) != int):
                utils.prRed(
                    "❌ No resume has been selected please add at least one resume to your Linkedin account.")
        except:
            pass

    def getJobProperties(self, count):
        textToWrite = ""
        jobTitle = ""
        jobLocation = ""

        try:
            jobTitle = self.driver.find_element(
                By.XPATH, "//h1[contains(@class, 'job-title')]").get_attribute("innerHTML").strip()
            res = [blItem for blItem in config.blackListTitles if (
                blItem.lower() in jobTitle.lower())]
            if (len(res) > 0):
                jobTitle += "(blacklisted title: " + ' '.join(res) + ")"
        except Exception as e:
            if (config.displayWarnings):
                utils.prYellow(
                    "⚠️ Warning in getting jobTitle: " + str(e)[0:50])
            jobTitle = ""

        try:
            time.sleep(5)
            jobDetail = self.driver.find_element(
                By.XPATH, "//div[contains(@class, 'job-details-jobs')]//div").text.replace("·", "|")
            res = [blItem for blItem in config.blacklistCompanies if (
                blItem.lower() in jobTitle.lower())]
            if (len(res) > 0):
                jobDetail += "(blacklisted company: " + ' '.join(res) + ")"
        except Exception as e:
            if (config.displayWarnings):
                print(e)
                utils.prYellow(
                    "⚠️ Warning in getting jobDetail: " + str(e)[0:100])
            jobDetail = ""

        try:
            jobWorkStatusSpans = self.driver.find_elements(
                By.XPATH, "//span[contains(@class,'ui-label ui-label--accent-3 text-body-small')]//span[contains(@aria-hidden,'true')]")
            for span in jobWorkStatusSpans:
                jobLocation = jobLocation + " | " + span.text

        except Exception as e:
            if (config.displayWarnings):
                print(e)
                utils.prYellow(
                    "⚠️ Warning in getting jobLocation: " + str(e)[0:100])
            jobLocation = ""

        textToWrite = str(count) + " | " + jobTitle + \
            " | " + jobDetail + jobLocation
        return textToWrite

    def easyApplyButton(self):
        try:
            time.sleep(random.uniform(1, constants.botSpeed))
            button = self.driver.find_element(
                By.XPATH, '//*[@data-view-name="job-apply-button"]')
            EasyApplyButton = button
        except:
            EasyApplyButton = False

        return EasyApplyButton

    def answerQuestions(self):
        """Executa o preenchimento automático do formulário."""
        # Mapeamento de seletores para funções
        selectors = {
            'div[data-test-text-entity-list-form-component]': self._fill_select,
            'div[data-test-single-line-text-form-component]': self._fill_input,
            'div[data-test-multiline-text-form-component]': self._fill_textarea,
            'fieldset[data-test-form-builder-radio-button-form-component="true"]': self._fill_radio,
        }

        for selector, handler in selectors.items():
            elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
            for el in elements:
                handler(el)
        # fieldset data-test-checkbox-form-component

    def _ask_gpt(self, prompt: str):
        try:
            response = self.client.responses.create(
                model="gpt-4.1-mini",
                temperature=0,
                input=[{
                    "role": "user",
                    "content": [{"type": "input_text", "text": prompt}],
                }],
                tools=[{
                    "type": "file_search",
                    "vector_store_ids": [self.vector_store.id],
                }],
            )

            for item in response.output:
                if item.type == "message":
                    for content in item.content:
                        if content.type == "output_text":
                            return content.text.strip()
        except Exception as e:
            self.utils.prRed(f"❌ Erro no GPT: {e}")
        return None

    def _fill_select(self, select_block):
        try:
            label = select_block.find_element(
                By.TAG_NAME, 'label').text.strip()
            select = Select(select_block.find_element(By.TAG_NAME, 'select'))

            options = [
                (i, o.text.strip()) for i, o in enumerate(select.options)
                if o.text.strip().lower() not in ("select an option", "none")
            ]

            if not options:
                return

            self.utils.prGreen('QUESTION', label)
            for idx, text in options:
                self.utils.prGreen(f"index: {idx} - value: {text}")

            options_text = "\n".join(
                [f"index: {i} - value: {v}" for i, v in options])
            prompt = (
                f"Você conhece o usuário e deve escolher uma opção do formulário de candidatura de vaga.\n\n"
                f"Pergunta: {label}\n\n"
                f"Possíveis respostas:\n{options_text}\n\n"
                "Responda **somente** com o número do index da melhor opção para garantir aprovação na vaga.\n"
                "Não escreva justificativas nem explicações."
            )

            answer = self._ask_gpt(prompt)
            if answer and answer.isdigit():
                idx = int(answer)
                select.select_by_index(idx)
                self.utils.prGreen(f"✅ Selecionado index: {idx}")
            else:
                self.utils.prRed(f"⚠️ Resposta inválida: {answer}")

        except Exception as e:
            self.utils.prRed(f"Erro ao processar select: {e}")

    def _fill_input(self, input_block):
        """Preenche campos <input>."""
        try:
            label = input_block.find_element(By.TAG_NAME, 'label').text.strip()
            input_element = input_block.find_element(By.TAG_NAME, 'input')

            prompt = (
                "Se perguntar a pretensão salarial e não ficar claro se é CLT ou PJ, informe CLT.\n"
                "Você conhece o usuário e deve responder à pergunta do formulário de candidatura de vaga.\n\n"
                f"Pergunta: {label}\n\n"
                "Escolha a melhor resposta para garantir a vaga.\n"
                "Se a pergunta for sobre anos, use apenas números.\n"
                "Se o usuário nunca trabalhou com essa tecnologia, responda com '10'.\n"
                "Não escreva explicações ou contexto."
            )

            answer = self._ask_gpt(prompt)
            if answer:
                input_element.clear()
                input_element.send_keys(answer)
                print(f"✅ Resposta: {answer}")
            else:
                print(f"⚠️ Sem resposta para: {label}")

        except Exception as e:
            print(f"Erro no input '{label}': {e}")

    def _fill_textarea(self, textarea_block):
        try:
            label = textarea_block.find_element(
                By.TAG_NAME, 'label').text.strip()
            textarea = textarea_block.find_element(By.TAG_NAME, 'textarea')

            prompt = (
                "Se perguntar a pretensão salarial e não ficar claro se é CLT ou PJ, informe CLT.\n"
                "Você conhece o usuário e deve responder à pergunta do formulário de candidatura de vaga.\n\n"
                f"Pergunta: {label}\n\n"
                "Escolha a melhor resposta para garantir a vaga.\n"
                "Se a pergunta for sobre anos, use apenas números.\n"
                "Se o usuário nunca trabalhou com essa tecnologia, responda com '10'.\n"
                "Não escreva explicações ou contexto."
            )

            answer = self._ask_gpt(prompt)
            if answer:
                textarea.clear()
                textarea.send_keys(answer)
                print(f"✅ Resposta: {answer}")
            else:
                print(f"⚠️ Sem resposta para: {label}")

        except Exception as e:
            print(f"Erro no textarea '{label}': {e}")

    def _fill_radio(self, radio_block):
        try:
            label = radio_block.find_element(
                By.TAG_NAME, 'legend').text.strip()
            radios = radio_block.find_elements(
                By.CSS_SELECTOR, "input[type='radio']")

            options = [
                f"index: {i} - value: {r.get_attribute('value')}" for i, r in enumerate(radios)]
            print("Pergunta:", label)
            for o in options:
                print(o)

            prompt = (
                f"Você conhece o usuário e deve escolher uma opção do formulário de candidatura.\n\n"
                f"Pergunta: {label}\n\n"
                f"Possíveis respostas:\n{chr(10).join(options)}\n\n"
                "Responda **somente** com o número do index da melhor opção para garantir aprovação na vaga.\n"
                "Não escreva texto adicional ou justificativas."
            )

            answer = self._ask_gpt(prompt)
            if not (answer and answer.isdigit()):
                print(f"⚠️ Resposta inválida: {answer}")
                return

            idx = int(answer)
            if idx < len(radios):
                radio = radios[idx]
                label_for = radio.get_attribute("id")
                label_elem = radio_block.find_element(
                    By.CSS_SELECTOR, f'label[for="{label_for}"]')
                label_elem.click()
                print(f"✅ Radio selecionado: {label_elem.text}")
            else:
                print(f"⚠️ Index {idx} fora do intervalo")

        except Exception as e:
            print(f"Erro ao processar radio: {e}")

    def applyProcess(self, percentage, offerPage):
        applyPages = math.floor(100 / percentage) - 2
        result = ""

        try:
            for pages in range(applyPages):
                self.driver.find_element(
                    By.CSS_SELECTOR, "button[aria-label='Continue to next step']").click()
        except:
            print('TEM PERGUNTAS OBRIGATORIAS')

        if self.driver.find_element(
                By.CSS_SELECTOR, "button[aria-label='Review your application']"):

            self.answerQuestions()

            self.driver.find_element(
                By.CSS_SELECTOR, "button[aria-label='Review your application']").click()
            time.sleep(random.uniform(1, constants.botSpeed))

            if config.followCompanies is False:
                try:
                    self.driver.find_element(
                        By.CSS_SELECTOR, "label[for='follow-company-checkbox']").click()
                except:
                    pass

            self.driver.find_element(
                By.CSS_SELECTOR, "button[aria-label='Submit application']").click()
            time.sleep(random.uniform(1, constants.botSpeed))

            result = "* 🥳 Just Applied to this job: " + str(offerPage)

            return result
        else:
            print('TEM PERGUNTAS OBRIGATORIAS')

    def displayWriteResults(self, lineToWrite: str):
        try:
            print(lineToWrite)
            utils.writeResults(lineToWrite)
        except Exception as e:
            utils.prRed("❌ Error in DisplayWriteResults: " + str(e))

    def element_exists(self, parent, by, selector):
        return len(parent.find_elements(by, selector)) > 0


start = time.time()
Linkedin().linkJobApply()
end = time.time()
utils.prYellow(
    "---Took: " + str(round((time.time() - start)/60)) + " minute(s).")
