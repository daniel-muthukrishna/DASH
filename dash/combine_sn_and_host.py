from dash.preprocessing import ReadSpectrumFile, ProcessingTools, PreProcessSpectrum
import matplotlib.pyplot as plt


class CombineSnAndHost(object):
    def __init__(self, snFile, galFile, w0, w1, nw):
        self.w0 = w0
        self.w1 = w1
        self.nw = nw
        self.numSplinePoints = 13
        self.processingTools = ProcessingTools()
        self.snReadSpectrumFile = ReadSpectrumFile(snFile, w0, w1, nw)
        self.galReadSpectrumFile = ReadSpectrumFile(galFile, w0, w1, nw)
        self.snSpectrum = self.snReadSpectrumFile.file_extension()
        self.galSpectrum = self.galReadSpectrumFile.file_extension()
        self.preProcess = PreProcessSpectrum(w0, w1, nw)

    def snid_sn_template_data(self, ageIdx):
        wave, fluxes, ncols, ages, ttype, splineInfo = self.snSpectrum
        # Undo continuum in the following step in preprocessing.py
        wave, flux = self.snReadSpectrumFile.snid_template_undo_processing(wave, fluxes[ageIdx], splineInfo)

        binnedWave, binnedFlux, minIndex, maxIndex = self.preProcess.log_wavelength(wave, flux)
        binnedFluxNorm = self._normalise_spectrum(binnedFlux)

        return binnedWave, binnedFluxNorm, minIndex, maxIndex

    def gal_template_data(self):
        wave, flux = self.galSpectrum

        # Limit bounds from w0 to w1 and normalise flux
        wave, flux = self.galReadSpectrumFile.two_col_input_spectrum(wave, flux, z=0)
        binnedWave, binnedFlux, minIndex, maxIndex = self.preProcess.log_wavelength(wave, flux)
        binnedFluxNorm = self._normalise_spectrum(binnedFlux)

        return binnedWave, binnedFluxNorm, minIndex, maxIndex

    def _normalise_spectrum(self, flux):
        fluxNorm = (flux - min(flux)) / (max(flux) - min(flux))

        return fluxNorm

    def overlapped_spectra(self, snAgeIdx):
        snWave, snFlux, snMinIndex, snMaxIndex = self.snid_sn_template_data(snAgeIdx)
        galWave, galFlux, galMinIndex, galMaxIndex = self.gal_template_data()

        minIndex = max(snMinIndex, galMinIndex)
        maxIndex = min(snMaxIndex, galMaxIndex)

        snWave = snWave[minIndex:maxIndex]
        snFlux = snFlux[minIndex:maxIndex]
        galWave = galWave[minIndex:maxIndex]
        galFlux = galFlux[minIndex:maxIndex]

        return (snWave, snFlux), (galWave, galFlux)


    def sn_plus_gal(self, snCoeff, galCoeff, snAgeIdx):
        (snWave, snFlux), (galWave, galFlux) = self.overlapped_spectra(snAgeIdx)

        combinedFlux = (snCoeff * snFlux) + (galCoeff * galFlux)

        return snWave, combinedFlux


if __name__ == '__main__':
    fSN = '/Users/danmuth/PycharmProjects/DASH/templates/snid_templates_Modjaz_BSNIP/sn2001br.lnw'
    fGal = '/Users/danmuth/PycharmProjects/DASH/templates/superfit_templates/gal/Sa'
    combine = CombineSnAndHost(fSN, fGal, 2500, 10000, 1024)

    f = plt.figure()
    xSN, ySN, minSN, maxSN = combine.snid_sn_template_data(ageIdx=0)
    xGal, yGal, minGal, maxGal = combine.gal_template_data()
    plt.plot(xSN, ySN, 'b.')
    plt.plot(xGal, yGal, 'r.')

    f2 = plt.figure()
    (xSN, ySN), (xGal, yGal) = combine.overlapped_spectra(0)
    xCombined, yCombined =  combine.sn_plus_gal(0.3, 0.7, 0)
    plt.plot(xSN, ySN, 'b.')
    plt.plot(xGal, yGal, 'r.')
    plt.plot(xCombined, yCombined, 'g.')


    galNames = ['E', 'S0', 'Sa', 'Sb', 'Sc', 'SB1', 'SB2', 'SB3', 'SB4', 'SB5', 'SB6',]
    fGals = ['/Users/danmuth/PycharmProjects/DASH/templates/superfit_templates/gal/E',
            '/Users/danmuth/PycharmProjects/DASH/templates/superfit_templates/gal/S0',
            '/Users/danmuth/PycharmProjects/DASH/templates/superfit_templates/gal/Sa',
            '/Users/danmuth/PycharmProjects/DASH/templates/superfit_templates/gal/Sb',
            '/Users/danmuth/PycharmProjects/DASH/templates/superfit_templates/gal/Sc',
            '/Users/danmuth/PycharmProjects/DASH/templates/superfit_templates/gal/SB1',
            '/Users/danmuth/PycharmProjects/DASH/templates/superfit_templates/gal/SB2',
            '/Users/danmuth/PycharmProjects/DASH/templates/superfit_templates/gal/SB3',
            '/Users/danmuth/PycharmProjects/DASH/templates/superfit_templates/gal/SB4',
            '/Users/danmuth/PycharmProjects/DASH/templates/superfit_templates/gal/SB5',
            '/Users/danmuth/PycharmProjects/DASH/templates/superfit_templates/gal/SB6',]


    for i in range(len(fGals)):
        f3 = plt.figure()
        combine = CombineSnAndHost(fSN, fGals[i], 2500, 10000, 1024)
        xGal, yGal, minGal, maxGal = combine.gal_template_data()
        plt.plot(xGal, yGal)
        plt.savefig("%s.png" % galNames[i])

    plt.show()




